// Cut a person out of a photo and turn it into a black halftone graphic (like the cover silhouette).
// Uses macOS Vision (no extra software).
//   swift tools/cutout.swift <photo> <out.png> [max height px] [dot cell px] [shadow lift, e.g. 0.55 for dark clothes]
//   dot cell 0 = a plain colour cut-out (no halftone)
import AppKit
import CoreImage
import Vision

let a = CommandLine.arguments
guard a.count >= 3 else { print("usage: cutout.swift <photo> <out.png> [maxHeight] [cell]"); exit(1) }
let maxH = a.count > 3 ? CGFloat(Double(a[3])!) : 1800
let cell = a.count > 4 ? CGFloat(Double(a[4])!) : 9
let lift = a.count > 5 ? Double(a[5])! : 1

// 1) load + downscale
var input = CIImage(contentsOf: URL(fileURLWithPath: a[1]), options: [.applyOrientationProperty: true])!
let scale = min(1, maxH / input.extent.height)
input = input.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
let ctx = CIContext()
let cg = ctx.createCGImage(input, from: input.extent)!

// 2) foreground mask (the person, including the motion blur around them)
let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(cgImage: cg)
try! handler.perform([req])
guard let obs = req.results?.first else { print("no person found"); exit(1) }
let maskBuf = try! obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler)
let mask = CIImage(cvPixelBuffer: maskBuf)

// 3) grayscale with a bit of contrast
let gray = input.applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: 0, kCIInputContrastKey: 1.25, kCIInputBrightnessKey: 0.04])
    .applyingFilter("CIGammaAdjust", parameters: ["inputPower": lift])
let W = Int(input.extent.width), H = Int(input.extent.height)
func pixels(_ img: CIImage) -> [UInt8] {
    var buf = [UInt8](repeating: 0, count: W * H * 4)
    ctx.render(img, toBitmap: &buf, rowBytes: W * 4, bounds: CGRect(x: 0, y: 0, width: W, height: H),
               format: .RGBA8, colorSpace: CGColorSpaceCreateDeviceRGB())
    return buf
}
let g = pixels(gray.cropped(to: CGRect(x: 0, y: 0, width: W, height: H)))
let m = pixels(mask.cropped(to: CGRect(x: 0, y: 0, width: W, height: H)))

// stretch the tones found inside the figure to the full range (keeps detail in dark clothes)
var tones: [UInt8] = []
for i in stride(from: 0, to: g.count, by: 16) where m[i] > 120 { tones.append(g[i]) }
tones.sort()
let lo = tones.isEmpty ? 0 : CGFloat(tones[tones.count * 3 / 100]) / 255
let hi = tones.isEmpty ? 1 : CGFloat(tones[tones.count * 97 / 100]) / 255

// colour cut-out: the photo itself, transparent around the figure
if cell == 0 {
    let cut = input.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: CIImage.empty(), kCIInputMaskImageKey: mask])
    var minX = W, minY = H, maxX = 0, maxY = 0
    for y in 0..<H { for x in 0..<W where m[(y * W + x) * 4] > 90 {
        minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y) } }
    // CIImage origin is bottom-left
    let box = CGRect(x: minX, y: H - maxY - 1, width: maxX - minX + 1, height: maxY - minY + 1)
    let outCG = ctx.createCGImage(cut, from: box, format: .RGBA8, colorSpace: CGColorSpaceCreateDeviceRGB())!
    try! NSBitmapImageRep(cgImage: outCG).representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
    print("written colour \(Int(box.width))x\(Int(box.height))")
    exit(0)
}

// 4) halftone: a dot per cell on a 45° grid, bigger where darker, only inside the mask
let out = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0,
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
out.setFillColor(CGColor(red: 0.08, green: 0.08, blue: 0.08, alpha: 1))
let ang = CGFloat.pi / 4, c = cos(ang), s = sin(ang)
let span = CGFloat(max(W, H)) * 1.5
var u = -span
while u < span {
    var v = -span
    while v < span {
        let x = u * c - v * s + CGFloat(W) / 2, y = u * s + v * c + CGFloat(H) / 2
        let xi = Int(x), yi = Int(y)
        if xi >= 0, yi >= 0, xi < W, yi < H {
            let i = (yi * W + xi) * 4   // bitmap rows are top-down; CGContext is bottom-up
            let alpha = CGFloat(m[i]) / 255
            if alpha > 0.35 {
                let lum = min(1, max(0, (CGFloat(g[i]) / 255 - lo) / max(0.05, hi - lo)))
                let r = cell * 0.62 * sqrt(max(0, 1 - lum)) * min(1, alpha * 1.4)
                if r > 0.5 { out.fillEllipse(in: CGRect(x: x - r, y: CGFloat(H) - y - r, width: 2 * r, height: 2 * r)) }
            }
        }
        v += cell
    }
    u += cell
}
// 5) crop to the figure (+ a small margin)
var minX = W, minY = H, maxX = 0, maxY = 0
for y in 0..<H { for x in 0..<W where m[(y * W + x) * 4] > 90 {
    minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y) } }
let pad = Int(cell * 2)
let box = CGRect(x: max(0, minX - pad), y: max(0, minY - pad),
                 width: min(W, maxX + pad) - max(0, minX - pad), height: min(H, maxY + pad) - max(0, minY - pad))
let rep = NSBitmapImageRep(cgImage: out.makeImage()!.cropping(to: box)!)
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
print("written \(W)x\(H)")
