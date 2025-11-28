from lib.ImageComparision import compare_images

res = compare_images('screenshots_before.png', 'screenshots_after.png', output_dir='output', method='ssim', align=True, min_area=1500)
print(f"SSIM Score: {res.ssim_score}, Changed Percent: {res.changed_percent:.4f}, Regions Detected: {res.regions_count}, Output Paths: {res.output_paths}")