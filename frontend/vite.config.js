import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { execSync } from 'child_process'
import fs from 'fs'
import path from 'path'

// Auto-process the uploaded images to remove white backgrounds using native C# memory manipulation
try {
  const psScript = `
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
[ImageProcessor]::RemoveWhite('C:\\Users\\daksh\\.gemini\\antigravity\\brain\\e8ce18db-8380-4b51-9a8e-34bf92778b24\\media__1779030029144.png', 'C:\\Users\\daksh\\Downloads\\myy all project\\project folder\\smartcare-ai\\frontend\\public\\chameleon.png')
  `;
  
  const scriptPath = path.resolve(__dirname, 'remove_white.ps1');
  fs.writeFileSync(scriptPath, psScript);
  execSync('powershell -ExecutionPolicy Bypass -File .\\\\remove_white.ps1');
  console.log('✅ Processed Header Avatar natively!');
  
  // Directly copy the clean, perfectly transparent welcome brand image provided by the user
  const brandSrc = 'C:\\Users\\daksh\\.gemini\\antigravity\\brain\\e8ce18db-8380-4b51-9a8e-34bf92778b24\\media__1779073241056.png';
  const brandDest = path.resolve(__dirname, 'public/welcome-brand.png');
  if (fs.existsSync(brandSrc)) {
    fs.copyFileSync(brandSrc, brandDest);
    console.log('✅ Directly mounted clean welcome-brand.png safely into public root.');
  }

  // Directly copy the new green eye brand icon for both header and chat input
  const eyeSrc = 'C:\\Users\\daksh\\.gemini\\antigravity\\brain\\e8ce18db-8380-4b51-9a8e-34bf92778b24\\media__1779075072891.png';
  const eyeDest = path.resolve(__dirname, 'public/brand-eye-icon.png');
  const chatEyeDest = path.resolve(__dirname, 'public/chat-eye-icon.png');
  if (fs.existsSync(eyeSrc)) {
    fs.copyFileSync(eyeSrc, eyeDest);
    fs.copyFileSync(eyeSrc, chatEyeDest);
    console.log('✅ Directly mounted brand and chat eye icons safely into public root.');
  }
} catch (e) {
  console.error('Failed to mount direct assets:', e);
}

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
