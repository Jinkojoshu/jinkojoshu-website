// Video frames without ffmpeg (uses macOS AVFoundation).
//   Contact sheet to choose from:  swift tools/frames.swift sheet  <video> <out.jpg> [count]
//   One frame as a thumbnail:      swift tools/frames.swift frame  <video> <out.jpg> <seconds>
import AVFoundation
import AppKit

let args = CommandLine.arguments
guard args.count >= 4 else { print("usage: frames.swift sheet|frame <video> <out.jpg> [count|seconds]"); exit(1) }
let asset = AVURLAsset(url: URL(fileURLWithPath: args[2]))
let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = .zero
gen.requestedTimeToleranceAfter = .zero
let duration = CMTimeGetSeconds(asset.duration)

func frame(at s: Double, maxSize: CGFloat) -> CGImage? {
    gen.maximumSize = CGSize(width: maxSize, height: maxSize)
    return try? gen.copyCGImage(at: CMTime(seconds: s, preferredTimescale: 600), actualTime: nil)
}

func save(_ img: CGImage, _ path: String) {
    let rep = NSBitmapImageRep(cgImage: img)
    let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.85])!
    try! data.write(to: URL(fileURLWithPath: path))
}

if args[1] == "frame" {
    guard let img = frame(at: Double(args[4])!, maxSize: 1350) else { print("no frame"); exit(1) }
    save(img, args[3])
} else {
    let count = args.count > 4 ? Int(args[4])! : 24
    let cols = 6, rows = (count + cols - 1) / cols
    let first = frame(at: 0.1, maxSize: 320)!
    let w = first.width, h = first.height, label = 22
    let ctx = CGContext(data: nil, width: cols * w, height: rows * (h + label), bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setFillColor(NSColor.black.cgColor)
    ctx.fill(CGRect(x: 0, y: 0, width: cols * w, height: rows * (h + label)))
    NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)
    for i in 0..<count {
        let s = duration * (Double(i) + 0.5) / Double(count)
        guard let img = frame(at: s, maxSize: 320) else { continue }
        let x = (i % cols) * w, y = (rows - 1 - i / cols) * (h + label)
        ctx.draw(img, in: CGRect(x: x, y: y + label, width: w, height: h))
        NSString(string: String(format: "%.1fs", s)).draw(at: NSPoint(x: x + 4, y: y + 3),
            withAttributes: [.foregroundColor: NSColor.white, .font: NSFont.boldSystemFont(ofSize: 15)])
    }
    save(ctx.makeImage()!, args[3])
}
