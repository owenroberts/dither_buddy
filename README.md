Blender file and script to add dither to noise for animation backgrounds.

How to use
- Run blender from command line
- Set *Divisor* in *Shading* tab node editor --> higher means noise move slower
- Set resolution in blender *Output* settings
- Set dither algorithm style, factor number (higher means more colors, takes longer), and whether to randomize inputs
	- Later, add range of randomness
- Run *dither_render.py*
- Renders pngs and adds a image sequence to VSE timeline (uses algo name and factor in file name, overwrites previous images with same params)
- Preview and render
	- Add auto render for command line use
		- With auto image sequence delete


Later
- Add script to run a bunch of tests with time stamps