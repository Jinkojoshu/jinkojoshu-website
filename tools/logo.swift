// Brand logo → clean white silhouette on transparent (also removes fake "checkerboard" backgrounds).
//   swift tools/logo.swift <logo> <out.png>
import AppKit
let a = CommandLine.arguments
let img = NSImage(contentsOfFile: a[1])!
let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil)!
let W = cg.width, H = cg.height
var px = [UInt8](repeating: 0, count: W * H * 4)
let ctx = CGContext(data: &px, width: W, height: H, bitsPerComponent: 8, bytesPerRow: W * 4,
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: W, height: H))
// a real transparent logo (lots of clear pixels) keeps its own shape; otherwise the shape is "what isn't white/grey"
var clear = 0
for i in stride(from: 3, to: px.count, by: 4) where px[i] < 20 { clear += 1 }
let useAlpha = clear > W * H / 5
for i in stride(from: 0, to: px.count, by: 4) {
    let al = Double(px[i + 3]) / 255
    var ink = al
    if !useAlpha {
        let r = Double(px[i]) / 255, g = Double(px[i + 1]) / 255, b = Double(px[i + 2]) / 255
        let mx = max(r, g, b), mn = min(r, g, b)
        let sat = mx - mn, lum = (r + g + b) / 3
        ink = min(1, max(0, (0.72 - lum) * 4) + max(0, (sat - 0.12) * 3))
    }
    let o = UInt8(max(0, min(255, ink * 255)))
    px[i] = o; px[i + 1] = o; px[i + 2] = o; px[i + 3] = o   // premultiplied white
}
let out = ctx.makeImage()!
// trim empty edges
var minX = W, minY = H, maxX = 0, maxY = 0
for y in 0..<H { for x in 0..<W where px[(y * W + x) * 4 + 3] > 40 {
    minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y) } }
let crop = out.cropping(to: CGRect(x: minX, y: minY, width: maxX - minX + 1, height: maxY - minY + 1))!
try! NSBitmapImageRep(cgImage: crop).representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
