## Create a server that takes files to upload 
## and displays a visual representation of the molecule 
## 
## Running the program:
## > python3 server.py 56760
##
from MolDisplay import Molecule
import sys;
from http.server import HTTPServer, BaseHTTPRequestHandler;
import molsql
import urllib
import cgi
import io
import json
import MolDisplay
import molecule
import re
# list of files that we allow the web-server to serve to clients
# (we don't want to serve any file that the client requests)
public_files = [ '/index.html', '/upload_page.html','/list_mol.html','/viewer.html','/home_page.html','/style.css', '/script.js', '/upload_page.js',"/list_mol.js", "/home_page.js", "/viewer.js" ];
db = molsql.Database(reset=True)
db.create_tables()
class sub_handler ( BaseHTTPRequestHandler ):
	curr_mol = ""
	x = 0
	y = 0
	z = 0
	def do_GET(self):
		if self.path in public_files:
			self.send_response( 200 ); # OK
			self.send_header( "Content-type", "text/html" )
			fp = open( self.path[1:] ); 
            # [1:] to remove leading / so that file is found in current dir
			# load the specified file
			page = fp.read()
			fp.close(); 
			self.send_header( "Content-length", len(page) )
			self.end_headers()
			self.wfile.write( bytes( page, "utf-8" ) )
		elif (self.path == '/home_page.html'):
			self.send_response( 200 ); # OK
			self.send_header( "Content-type", "text/html" )
		elif self.path == "/display_element_list":
			elements = db.element_name()

			self.send_response(200) # OK
			self.send_header("Content-type", "application/json")
			self.end_headers()
			elements_json = json.dumps(elements)
			self.wfile.write(bytes(elements_json, "utf-8"))			
		elif self.path == '/list_mol':
			# get molecules data
			molecules = db.get_molecules()
			if len(molecules) == 0:
				# database empty
				self.send_response(204) # No Content
				self.send_header("Content-type", "application/json")
				self.end_headers()
				return
			self.send_response(200) # OK
			self.send_header("Content-type", "application/json")
			self.end_headers()
			molecules_json = json.dumps(molecules)
			self.wfile.write(bytes(molecules_json, "utf-8"))			
		
		elif(self.path == '/createMol'):
			if (sub_handler.curr_mol == ""):
				# database empty
				self.send_response(204) # No Content
				self.send_header("Content-type", "image/svg+xml")
				self.end_headers()
				return

			self.send_response( 200 ) # OK
			self.send_header("Content-type", "image/svg+xml") #Declare content type (image display)
			self.end_headers() #End declaration

			#length = int(self.headers.get('Content-Length', 0)) #Declare length of page
			# Get molecule and setup SVG
			MolDisplay.radius = db.radius()
			MolDisplay.element_name = db.element_name()
			MolDisplay.header += db.radial_gradients()
			mol = db.load_mol(sub_handler.curr_mol)

			if (sub_handler.x != 0):
				mx = molecule.mx_wrapper(int(sub_handler.x), 0, 0)
				mol.xform( mx.xform_matrix )
			if (sub_handler.y != 0):
				mx = molecule.mx_wrapper(0, int(sub_handler.y), 0)
				mol.xform( mx.xform_matrix )
			if (sub_handler.z != 0):
				mx = molecule.mx_wrapper(0, 0, int(sub_handler.z))
				mol.xform( mx.xform_matrix )
			mol.sort()
			self.wfile.write( bytes( mol.svg(), "utf-8" ) ) #Create Page
		else:
			self.send_response( 404 )
			self.end_headers()
			self.wfile.write( bytes( "404: not found", "utf-8" ) );
			
	def do_POST(self):
		if self.path == "/upload_form.html":
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD': 'POST'}
			)

			molName = form['mol-name'].value
			sdfFile = form['sdf-file'].value

			# Validate SDF extention
			content_disposition = form['sdf-file'].headers['Content-Disposition']
			filename = cgi.parse_header(content_disposition)[1]['filename']
			extension = filename.split('.')[-1]
			if extension != 'sdf':
				# Handle invalid SDF file error
				response_body = "Invalid SDF file"
				response_length = len(response_body.encode('utf-8'))
				self.send_response(400)
				self.send_header("Content-type", "text/plain")
				self.send_header("Content-length", response_length)
				self.end_headers()
				self.wfile.write(response_body.encode('utf-8'))
				return
			# Create Molecule
			tFile = io.BytesIO(sdfFile)
			file = io.TextIOWrapper(tFile)

			# Add molecule into database
			db.add_molecule(molName, file)
			# Send response to client
			
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			self.wfile.write(response_body.encode('utf-8'))
		
		elif self.path == "/form_handler.html":
			
			content_length = int(self.headers['Content-Length']);
			body = self.rfile.read(content_length)
			postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )
			operation = postvars['operation'][0]
			if (operation == "add"):
				# Parse for data
				element_code = postvars['eCode'][0]
				element_num = postvars['eNumber'][0]
				element_name = postvars['eName'][0]
				col1 = postvars['col1'][0]
				col2 = postvars['col2'][0]
				col3 = postvars['col3'][0]
				radius = postvars['rad'][0]
				
				regex = "/^[a-zA-Z0-9_\-]+$/;"
				if (re.match(regex, element_code)):
					print(element_code)
					self.send_response(404)
					self.end_headers()
					return 
				# Store Data
				element_tuple = (element_num, element_code, element_name, col1, col2, col3, radius)
				db['Elements'] = element_tuple
				print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
				self.send_response(200)
				self.end_headers()

			elif(operation == "remove"):
				new_dict = dict((v, k) for k, v in db.element_name().items())
				element_name = postvars['reCode'][0]
				element_code = new_dict[element_name]
				if (db.check_element_exists(element_code, element_name)):
					db.remove_element(element_name,element_code)
					self.send_response(200)
				else:
					self.send_response(404)
				print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
				self.end_headers()
		elif (self.path == "/viewer"):
			content_length = int(self.headers['Content-Length'])
			body = self.rfile.read(content_length)

			postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

			name = str(postvars['name'][0])
			# save molecule name globally
			sub_handler.curr_mol = name
			#reset the angles
			sub_handler.x = 0
			sub_handler.y = 0
			sub_handler.z = 0

			#readd elements if needed
			db.add_elements(name)
			
			# Send success response
			response_body = "Molecule saved"
			response_length = len(response_body.encode('utf-8'))
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.send_header("Content-length", response_length)
			self.end_headers()
			self.wfile.write(response_body.encode('utf-8'))	
		elif self.path == "/rotate":
			content_length = int(self.headers['Content-Length'])
			body = self.rfile.read(content_length)
			postvars = urllib.parse.parse_qs(body.decode('utf-8'))

			rotation_axis = postvars['dimension'][0]
			degree = 10
			if (rotation_axis == "x"):
				sub_handler.x = (sub_handler.x + degree) % 360
			elif (rotation_axis == "y"):
				sub_handler.y = (sub_handler.y + degree) % 360
			elif (rotation_axis == "z"):
				sub_handler.z = (sub_handler.z + degree) % 360

			# Send success response
			response_body = "Degree changed incremented successfully"
			response_length = len(response_body.encode('utf-8'))
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.send_header("Content-length", response_length)
			self.end_headers()
			self.wfile.write(response_body.encode('utf-8'))
		else:
			self.send_response( 404 )
			self.end_headers()
			self.wfile.write( bytes( "404: not found", "utf-8" ) );
      

httpd = HTTPServer( ( "localhost", int(sys.argv[1]) ), sub_handler );
httpd.serve_forever()



