import os;
import sqlite3;
import MolDisplay

class Database:
    
    def __init__( self, reset=False ):
        # for testing only; remove this for real usage
        if os.path.exists( "molecules.db" ) and reset == True:
            os.remove( "molecules.db" )
        # create database file if it doesn't exist and connect to it
        self.conn = sqlite3.connect( "molecules.db" )

    def get_molecules(self):
        # Open Connection
        conn = sqlite3.connect('molecules.db')
        cursor = conn.cursor()

        # Select Molecule IDs, Names, Bond Counts, and Atom Counts
        query1 = """SELECT Molecules.MOLECULE_ID, Molecules.NAME, COUNT(DISTINCT Bonds.BOND_ID), COUNT(DISTINCT Atoms.ATOM_ID)
                    FROM Molecules
                    JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                    JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID
                    JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                    JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
                    GROUP BY Molecules.MOLECULE_ID"""
        cursor.execute(query1)
        molecule_results = cursor.fetchall()

        molecule_info = []

        # Loop Through Molecules
        for molecule_result in molecule_results:
            name = molecule_result[1]
            bond_count = molecule_result[2]
            atom_count = molecule_result[3]

            # Create Molecule Dictionary
            molecule = {
                "name": name,
                "bond_count": bond_count,
                "atom_count": atom_count
            }

            # Append Molecule to List
            molecule_info.append(molecule)

        # Close Connection
        cursor.close()
        conn.close()

        return molecule_info

    
    #Check if the passed element exists
    def check_element_exists(self, element_code, element_name):
        c = self.conn.cursor()
        c.execute("SELECT element_code FROM Elements WHERE EXISTS(SELECT element_code FROM Elements WHERE element_code=?)", (element_code,))
        c.execute("SELECT element_name FROM Elements WHERE EXISTS(SELECT element_name FROM Elements WHERE element_name=?)", (element_name,))
        row = c.fetchall()
        if len(row) >= 1:
            return True
        else:
            return False

    # Remove the element from the passed argument   
    def remove_element(self, element_name, element_code):  
        c = self.conn.cursor()
        c.execute("DELETE FROM Elements WHERE element_name=?", (element_name,))
        c.execute("DELETE FROM Elements WHERE element_code=?", (element_code,))
        self.conn.commit()
        self.conn.close
        
    
    def create_tables(self):
        #Elements table
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Elements
                                    ( ELEMENT_NO    INTEGER NOT NULL,
                                      ELEMENT_CODE  VARCHAR(3) PRIMARY KEY NOT NULL,
                                      ELEMENT_NAME  VARCHAR(32) NOT NULL,
                                      COLOUR1       CHAR(6) NOT NULL,
                                      COLOUR2       CHAR(6) NOT NULL,
                                      COLOUR3       CHAR(6) NOT NULL,
                                      RADIUS        DECIMAL(3) NOT NULL );""" )
        #Atoms table
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Atoms
                                    ( ATOM_ID       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                      ELEMENT_CODE  VARCHAR(3) NOT NULL REFERENCES Elements(ELEMENT_CODE),
                                      X             DECIMAL(7,4) NOT NULL,
                                      Y             DECIMAL(7,4) NOT NULL,
                                      Z             DECIMAL(7,4) NOT NULL );""" )

        #Bonds table
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Bonds
                                    ( BOND_ID       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                      A1            INTEGER NOT NULL,
                                      A2            INTEGER NOT NULL,
                                      EPAIRS        INTEGER NOT NULL );""" )

        #Molecules table
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Molecules
                                    ( MOLECULE_ID   INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                      NAME          TEXT UNIQUE NOT NULL );""")

        #moleculeAtom table
        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeAtom
                                    ( MOLECULE_ID INTEGER NOT NULL,
                                      ATOM_ID INTEGER NOT NULL,
                                      PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                                      FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                                      FOREIGN KEY (ATOM_ID) REFERENCES Atoms );""")

        #moleculeBond table
        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeBond
                                    ( MOLECULE_ID INTEGER NOT NULL,
                                      BOND_ID INTEGER NOT NULL,
                                      PRIMARY KEY (MOLECULE_ID, BOND_ID),
                                      FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                                      FOREIGN KEY (BOND_ID) REFERENCES Bonds );""")


    def __setitem__( self, table, values ):
        # set tables based on tuple

        # Elements Table
        if table == "Elements": 
            self.conn.execute(f"""INSERT
                                  INTO   Elements
                                  VALUES ('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}', '{values[4]}','{values[5]}', '{values[6]}');""")

        # Atoms table
        if table == "Atoms":
            self.conn.execute(f"""INSERT
                                  INTO   Atoms
                                  VALUES ('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}', '{values[4]}');""")


        # Bonds table
        if table == "Bonds":
            self.conn.execute(f"""INSERT
                                  INTO   Bonds
                                  VALUES ('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}');""")

        # Molecule table
        if table == "Molecules": 
            self.conn.execute(f"""INSERT
                                  INTO   Molecules
                                  VALUES ('{values[0]}', '{values[1]}');""")

        # moleculeAtom table
        if table == "MoleculeAtom": 
            self.conn.execute(f"""INSERT
                                  INTO   MoleculeAtom
                                  VALUES ('{values[0]}', '{values[1]}');""")

        # moleculeBond table
        if table == "MoleculeBond":
            self.conn.execute(f"""INSERT
                                   INTO   MoleculeBond
                                   VALUES ('{values[0]}', '{values[1]}');""")


    def add_atom( self, molname, atom ):
        # insert atom values into table
        self.conn.execute( f"""INSERT 
                            INTO Atoms 
                            VALUES (null, '%s', %f, %f, %f) """ % (atom.c_atom.element, atom.c_atom.x, atom.c_atom.y, atom.c_atom.z))
        self.conn.commit()

        # Get mol and atom ID
        molecule_ID = self.conn.execute(f"""SELECT Molecules.MOLECULE_ID FROM Molecules WHERE Molecules.NAME = '{molname}'""")
        atom_ID = self.conn.execute("""SELECT * FROM Atoms WHERE ATOM_ID = (SELECT MAX(ATOM_ID) FROM Atoms)""")
        
        #set the row to the atom ID
        row = atom_ID
        atom_ID = row.fetchone()[0]

        # set the molIndex to the molecule ID
        mol_index = molecule_ID
        molecule_ID =  mol_index.fetchone()[0]

        # Insert ID's into Table
        self.conn.execute("""INSERT INTO MoleculeAtom VALUES (%d, %d) """ % (molecule_ID, atom_ID))
        self.conn.commit()

    def add_bond( self, molname, bond ):
        # add bond values
        self.conn.execute( f"""INSERT 
                                INTO Bonds 
                                VALUES  (null, %f, %f, %f) """ % (bond.c_bond.a1, bond.c_bond.a2, bond.c_bond.epairs))
        self.conn.commit()

        # set the molecule ID and bond ID
        molecule_ID = self.conn.execute( f"""SELECT Molecules.MOLECULE_ID FROM Molecules WHERE Molecules.NAME = '{molname}'""")
        bond_ID = self.conn.execute("""SELECT * FROM Bonds WHERE BOND_ID = (SELECT MAX(BOND_ID) FROM Bonds)""")
        
        #sets row and bondID
        row = bond_ID
        bond_ID = row.fetchone()[0]
        
        #sets molIndex and moleculeID
        mol_index = molecule_ID
        molecule_ID =  mol_index.fetchone()[0]

        # Insert ID's into Table
        self.conn.execute(f"""INSERT 
                              INTO MoleculeBond 
                              VALUES ('{molecule_ID}', '{bond_ID}')""")

        # Commit the change
        self.conn.commit()

    # method to add molecule
    def add_molecule(self, name, fp):
        mol_dict = self.get_molecules()
        if name in mol_dict:
            return
        molec = MolDisplay.Molecule()
        molec.parse(fp)

        self.conn.execute(f"""INSERT
                              INTO   Molecules
                              VALUES (null, '{name}');""")
        self.conn.commit()
        #add bonds & atoms
        #add in default values if needed

        for i in range(molec.bond_no):
            bond = MolDisplay.Bond(molec.get_bond(i))
            self.add_bond(name, bond)
        for i in range(molec.atom_no):
            atom = MolDisplay.Atom(molec.get_atom(i))
            self.add_atom(name, atom)
            
        print(self.element_name())        
        self.add_elements(name)


    def add_elements(self, molname):
        molec = self.load_mol(molname)
        # new_dict = dict((v, k) for k, v in self.element_name().items())
        #print(self.element_name())        
        for i in range(molec.atom_no):
            atom = MolDisplay.Atom(molec.get_atom(i))
            elem_name = ""
            if atom.c_atom.element in  self.element_name():
                elem_name = self.element_name()[atom.c_atom.element]
            if (not(self.check_element_exists(atom.c_atom.element, elem_name))):
                self.conn.execute(f"""INSERT
                                    INTO   Elements
                                    VALUES ('{999}', '{atom.c_atom.element}', '{atom.c_atom.element}', '#40E0D0', '#F5DEB3','#FFFFFF', '{25}');""")
    
    def load_mol( self, name ):
        mol = MolDisplay.Molecule()
        cursor = self.conn.cursor()
        cursor.execute( f"""SELECT *
                            FROM Atoms, MoleculeAtom, Molecules
                            WHERE Atoms.ATOM_ID = MoleculeAtom.ATOM_ID AND Molecules.NAME = ? AND Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                            ORDER BY ATOM_ID ASC""", (name,))
        atoms_arr = cursor.fetchall()
        # loop through the atoms
        for atom in atoms_arr:
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])

        cursor.execute("""SELECT *
                            FROM Bonds, MoleculeBond, Molecules
                            WHERE Bonds.BOND_ID = MoleculeBond.BOND_ID AND Molecules.NAME = ? AND Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                            ORDER BY BOND_ID ASC""", (name,))
        bonds_arr = cursor.fetchall()

        # loop through the bonds
        for bond in bonds_arr:
            mol.append_bond(bond[1], bond[2], bond[3])

        # return molecule
        return mol

    def radius(self):
        cursor = self.conn.cursor()

        cursor.execute("""SELECT ELEMENT_CODE, RADIUS
                          FROM Elements""")
        
        data = cursor.fetchall()

        dictionary = dict(data)

        return dictionary
        
    def element_name(self):
        cursor = self.conn.cursor()

        cursor.execute("""SELECT ELEMENT_CODE, ELEMENT_NAME
                          FROM Elements""")
        
        data = cursor.fetchall()

        dictionary = dict(data)
        return dictionary
    
    def radial_gradients(self):
        radial_grad = ""
        cursor = self.conn.cursor()
        cursor.execute("""SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 
                          FROM Elements""")

        elements = cursor.fetchall()
        for element in elements:
            radial_grad = radial_grad + """
<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
  <stop offset="0%%" stop-color="%s"/>
  <stop offset="50%%" stop-color="%s"/>
  <stop offset="100%%" stop-color="%s"/>
</radialGradient>""" % (element[0], element[1], element[2], element[3])
        return radial_grad
    






