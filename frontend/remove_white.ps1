
$code = @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public class ImageProcessor {
    public static void RemoveWhite(string src, string dest) {
        try {
            using (Image img = Image.FromFile(src))
            using (Bitmap bmp = new Bitmap(img.Width, img.Height, PixelFormat.Format32bppArgb)) {
                using (Graphics g = Graphics.FromImage(bmp)) {
                    g.DrawImage(img, 0, 0, img.Width, img.Height);
                }
                BitmapData data = bmp.LockBits(new Rectangle(0, 0, bmp.Width, bmp.Height), ImageLockMode.ReadWrite, PixelFormat.Format32bppArgb);
                int bytes = Math.Abs(data.Stride) * bmp.Height;
                byte[] rgbValues = new byte[bytes];
                Marshal.Copy(data.Scan0, rgbValues, 0, bytes);
                
                for (int i = 0; i < rgbValues.Length; i += 4) {
                    byte b = rgbValues[i];
                    byte g = rgbValues[i + 1];
                    byte r = rgbValues[i + 2];
                    // If pixel is near-white, make it transparent
            if (r > 240 && g > 240 && b > 240) {
              rgbValues[i + 3] = 0; // Set alpha to 0
            }
          }

          System.Runtime.InteropServices.Marshal.Copy(rgbValues, 0, data.Scan0, bytes);
          bmp.UnlockBits(data);
          bmp.Save(dest, System.Drawing.Imaging.ImageFormat.Png);
        } catch {}
      }
    }
"@
Add-Type -TypeDefinition $code -ReferencedAssemblies System.Drawing
[ImageProcessor]::RemoveWhite('C:\Users\daksh\.gemini\antigravity\brain\e8ce18db-8380-4b51-9a8e-34bf92778b24\media__1779030029144.png', 'C:\Users\daksh\Downloads\myy all project\project folder\smartcare-ai\frontend\public\chameleon.png')
  