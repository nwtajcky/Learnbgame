import ocl
import tempfile
import camvtk
		
stl = camvtk.STLSurf(tempfile.gettempdir()+"/model0.stl")
stl_polydata = stl.src.GetOutput()
stl_surf = ocl.STLSurf()
camvtk.vtkPolyData2OCLSTL(stl_polydata, stl_surf)
csv_file = open(tempfile.gettempdir()+'/ocl_settings.txt','r')
op_cutter_type = csv_file.readline().split()[0]
op_cutter_diameter = float( csv_file.readline() )
op_minz = float( csv_file.readline() )
csv_file.close();

cutter_length = 150
if op_cutter_type == 'END':
	cutter = ocl.CylCutter( op_cutter_diameter*1000, cutter_length)
elif op_cutter_type == 'BALLNOSE':
	cutter = ocl.BallCutter( op_cutter_diameter*1000, cutter_length)
elif op_cutter_type == 'VCARVE':
	cutter = ocl.ConeCutter( op_cutter_diameter*1000, 1, cutter_length)
else:
	print "Cutter unsupported: " + op_cutter_type + '\n'
	quit()
wl_height_file = open( tempfile.gettempdir()+'/ocl_wl_heights.txt', 'r' )
waterline_heights = []
for line in wl_height_file:
	waterline_heights.append( float( line.split()[0] ) )
wl_height_file.close()
wl_index = 0
waterline = ocl.Waterline()
waterline.setSTL(stl_surf)
waterline.setCutter(cutter)
waterline.setSampling(0.1)
for height in waterline_heights:
	print( str(height) + '\n' )
	waterline.reset();
	waterline.setZ(height)
	waterline.run2()
	wl_loops = waterline.getLoops()
	wl_file = open( tempfile.gettempdir()+'/oclWaterline' + str(wl_index) + '.txt', 'w')
	for l in wl_loops:
		wl_file.write( 'l\n' )
		for p in l:
			wl_file.write( str(p.x) + ' '  + str(p.y) + ' '  + str(p.z) + '\n' )
	wl_file.close()
	wl_index += 1
