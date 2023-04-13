
import molecule;

header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""
offsetx = 500
offsety = 500

class Atom:

    def __init__ ( self, c_atom ):
        self.c_atom = c_atom
        self.z = c_atom.z

    def svg (self):
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (self.c_atom.x * 100 + offsetx, self.c_atom.y * 100 + offsety, radius[self.c_atom.element], element_name[self.c_atom.element])
    

class Bond:

    def __init__ ( self, c_bond ):
        self.c_bond = c_bond
        self.z = c_bond.z

    def __str__ (self):
        return "epairs: %d \nx1:%lf \ny1: %lf \nx2: %d \ny2:%lf \nz: %lf \nlen: %d \ndx:%lf \ndy: %lf" % (self.c_bond.epairs, self.c_bond.x1, self.c_bond.y1, self.c_bond.x2, self.c_bond.y2, self.c_bond.z, self.c_bond.len, self.c_bond.dx, self.c_bond.dy)
    
    def svg(self):
        #calculated centres of atoms relative to bonds
        atom1_x = self.c_bond.x1 * 100 + offsetx
        atom1_y = self.c_bond.y1 * 100 + offsety
        atom2_x = self.c_bond.x2 * 100 + offsetx
        atom2_y = self.c_bond.y2 * 100 + offsety
 
        #y-positions of atoms
        y1_upper = atom1_y + self.c_bond.dx * 10
        y1_lower = atom1_y - self.c_bond.dx * 10
        y2_upper = atom2_y + self.c_bond.dx * 10
        y2_lower = atom2_y - self.c_bond.dx * 10
        #x-positions of atoms
        x1_upper = atom1_x + self.c_bond.dy * 10
        x1_lower = atom1_x - self.c_bond.dy * 10
        x2_upper = atom2_x + self.c_bond.dy * 10
        x2_lower = atom2_x - self.c_bond.dy * 10
        
        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (x1_lower, y1_upper, x1_upper, 
            y1_lower, x2_upper, y2_lower, x2_lower, y2_upper)
    

class Molecule (molecule.molecule):
    
    def __str__(self):
        print("Atoms:")
        for atom in range (self.atom_no):
            print(self.get_atom(atom).element)

        print("Bonds:")
        for bond in range (self.bond_no):
            print(Bond(self.get_bond(bond)).__str__())

    def svg(self):
        list_atoms = []
        list_bonds = []

        #populate list of atoms
        for atom in range (self.atom_no):
            list_atoms.append(Atom(self.get_atom(atom)))
        #populate list of bonds
        for bond in range (self.bond_no):
            list_bonds.append(Bond(self.get_bond(bond)))
        
        #sort the list of atoms and bonds
        list_atoms.sort(key=lambda x: x.z)
        list_bonds.sort(key=lambda y: y.z)
        conc_str = header
        
        bond = 0
        atom = 0
        while bond < self.bond_no and atom < self.atom_no :
            atom_temp = list_atoms[atom]   
            bond_temp = list_bonds[bond]

            if atom_temp.z < bond_temp.z:
                conc_str += atom_temp.svg()
                atom+=1
            else:
                conc_str += bond_temp.svg()
                bond+=1
        
        #copy the remaining elements if needed
        while atom < self.atom_no:
            conc_str += list_atoms[atom].svg()
            atom+=1
        while bond < self.bond_no:
            conc_str += list_bonds[bond].svg()
            bond+=1

        conc_str += footer
        return conc_str
    
    def remove_spaces (self, arr_obj):
        for i in range (len(arr_obj)):
            if arr_obj[i].isspace():
                arr_obj.remove(i)

    def parse(self, file_obj):
        #ignoring non important info
        for i in range (3):
            file_obj.readline()
        # parsing line containing bond and atom no
        temp = file_obj.readline()
        # Removing trailing & leading spaces
        temp = temp.strip() 
        #parse string
        data = temp.split()
        self.remove_spaces(data)
        atom_no = int(data[0])
        bond_no = int(data[1])
        #appending atoms to molecle
        for i in range (atom_no):
            temp = file_obj.readline()
            temp = temp.strip()
            data_atoms = temp.split()
            #print(data_atoms)
            self.remove_spaces(data_atoms)
            x = float(data_atoms[0])
            y = float(data_atoms[1])
            z = float(data_atoms[2])
            name = str(data_atoms[3])
            
            #Checking and removing any unicode data
            if len(name) > 3:
                new_name = ""
                for i in name:
                    if (i.isupper()):
                        new_name += i
                self.append_atom(new_name, x, y, z)
            else:
                self.append_atom(name, x, y, z)
        
        #Appending bonds to the molecule
        for i in range (int(bond_no)):
            temp = file_obj.readline()
            temp = temp.strip()
            data_bonds = temp.split()
            self.remove_spaces(data_bonds)
            #print(data_bonds)
            atom1 = int(data_bonds[0])
            atom2 = int(data_bonds[1])
            epairs = int(data_bonds[2])

            atom1 = atom1 - 1
            atom2 = atom2 - 1
            self.append_bond( atom1, atom2, epairs )
    
        self.atom_no = atom_no
        self.bond_no = bond_no


    def add_molecule(self, name, fp):
        # Declare Object
        molecule = Molecule()
        # Parse file
        molecule.parse(fp)
        # Insert Molecule into table
        command = f"INSERT INTO Molecules (NAME) VALUES (?)"
        self.conn.execute(command, (name,))
        # Commit change
        self.conn.commit()

        # Add all atoms in Molecule
        for atoms in range(molecule.atom_no):
            self.add_atom(name, Atom(molecule.get_atom(atoms)))

        # Add all bonds in Molecule
        for bonds in range(molecule.bond_no):
            self.add_bond(name, Bond(molecule.get_bond(bonds)))
   