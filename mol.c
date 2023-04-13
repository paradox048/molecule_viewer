#include "mol.h"


rotations *spin( molecule *mol ) {
    return NULL;
}

void rotationsfree( rotations *rotations ) {
    printf("NOT DONE\n");
}

/**
 * @brief Sets the members within the passed atom to the provided arguments
 * 
 * @param atom 
 * @param element 
 * @param x 
 * @param y 
 * @param z 
 */
void atomset( atom *atom, char element[3], double *x, double *y, double *z ){
    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

/**
 * @brief copies the values of the members in the atom to the 
 *          corrosponding parameters pointers
 * 
 * @param atom 
 * @param element 
 * @param x 
 * @param y 
 * @param z 
 */
void atomget( atom *atom, char element[3], double *x, double *y, double *z ) {
    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    //new bondset
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;
    compute_coords(bond);
}

void compute_coords (bond * bond) {
    //x coord
    bond->x1 = bond->atoms[bond->a1].x;
    bond->x2 = bond->atoms[bond->a2].x;

    //y coord
    bond->y1 = bond->atoms[bond->a1].y;
    bond->y2 = bond->atoms[bond->a2].y;

    //calculate z
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z)/2;

    //calculate len
    bond->len = sqrt(pow((bond->x1 - bond->x2),2) + pow((bond->y1 - bond->y2),2));
    
    //calculate dx
    bond->dx = (bond->x2 - bond->x1) / bond->len;

    //calculate dy
    bond->dy = (bond->y2 - bond->y1) / bond->len;
}

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}

/**
 * @brief initializes a new molecule struct in memory and returns it
 * 
 * @param atom_max 
 * @param bond_max 
 * @return molecule* 
 */
molecule * molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    if (atom_max == 0) {
        atom_max = 1;
    }

    if (bond_max == 0) {
        bond_max = 1;
    }

    molecule * newMol = (molecule *)malloc(sizeof(molecule));
    newMol->atom_max = atom_max;
    newMol->atoms = (atom*)(malloc(sizeof(atom) * (atom_max)));
    newMol->atom_ptrs = (atom**)(malloc(sizeof(atom*) * (atom_max)));
    newMol->atom_ptrs[0] = newMol->atoms;
    newMol->atom_no = 0;

    
    newMol->bond_max = bond_max;
    newMol->bonds = (bond*)(malloc(sizeof(bond) * (bond_max)));;
    newMol->bond_ptrs = (bond**)(malloc(sizeof(bond*) * (bond_max)));
    newMol->bond_ptrs[0] = newMol->bonds;
    newMol->bond_no = 0;

    //checks for any invalid mallocs
    if (newMol == NULL || newMol->atoms == NULL || newMol->atom_ptrs == NULL || newMol->bonds == NULL|| newMol->bond_ptrs == NULL) {
        printf("Invalid Malloc Detected\n");
        exit(0);
    }
    return newMol;
}

/**
 * @brief copies the content from passed mol to new mol and returns the new mol
 * 
 * @param src 
 * @return molecule* 
 */
molecule * molcopy( molecule *src ) {
    //check if the src is null
    if (src == NULL) {
        return NULL;
    }

    molecule * newMol = molmalloc(src->atom_max, src->bond_max);
    //copies contents from src to newMol
    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom(newMol, &src->atoms[i]);
    }

    for (int j = 0; j < src->bond_no; j++) {
        molappend_bond(newMol, &src->bonds[j]);
    }
    return newMol;
}

void molfree( molecule *ptr) {

    if (ptr != NULL) {
        free(ptr->atoms);
        free(ptr->atom_ptrs);
        free(ptr->bonds);
        free(ptr->bond_ptrs);
        free(ptr);
    }
}

/**
 * @brief adds an atom to the end of the molecule atoms array
 * 
 * @param molecule 
 * @param atom 
 */
void molappend_atom( molecule *molecule, atom *atom) {
    //check if molecule is empty
    //check the size of atom max in molecule
    if (molecule == NULL) {
        molecule = molmalloc(0, 0);
    } else if (molecule->atom_no == 0) {
        molecule->atoms[0] = *atom;
        molecule->atom_no++;
    } else {
        //check if it is pointing to a random area of space
        if (molecule->atom_no + 1 > molecule->atom_max) {
            molecule->atom_max *= 2;
            molecule->atoms = (struct atom*)realloc(molecule->atoms, (sizeof(struct atom) * (molecule->atom_max)));
            molecule->atom_ptrs = (struct atom**)realloc(molecule->atom_ptrs, (sizeof(struct atom *) * (molecule->atom_max)));

            //checks if the malloc was successfull
            if (molecule->atoms == NULL || molecule->atom_ptrs == NULL) {
                printf("Invalid Malloc Detected \n");
                exit(0);
            }
        }

        //appends atom to ends of array
        molecule->atoms[(molecule->atom_no)] = *atom;
        molecule->atom_ptrs[(molecule->atom_no)] = atom;
        molecule->atom_no++;

        for (int i = 0; i < molecule->atom_max; i++) {
            molecule->atom_ptrs[i] = &molecule->atoms[i];
        }

    }
}

/**
 * @brief appends a bond to the molecule
 * 
 * @param molecule 
 * @param bond 
 */
void molappend_bond( molecule *molecule, bond *bond ) {
   //check if molecule is empty
    if (molecule == NULL) {
        molecule = molmalloc(0, 0);
    } else if (molecule->bond_no == 0) {
        molecule->bonds[0] = *bond;
        molecule->bond_no++;
    } else {
        //check if it is pointing to a random area of space

        if (molecule->bond_no + 1 > molecule->bond_max) {
            molecule->bond_max*=2;
            molecule->bonds = realloc(molecule->bonds, (sizeof(struct bond) * (molecule->bond_max)));
            molecule->bond_ptrs = realloc(molecule->bond_ptrs, (sizeof(struct bond *) * (molecule->bond_max))); 
            
            //checks if the malloc was successfull
            if (molecule->bonds == NULL || molecule->bond_ptrs == NULL) {
                printf("Invalid Malloc Detected \n");
                exit(0);
            }
        }
        //appends atom to ends of array
        molecule->bonds[(molecule->bond_no)] = *bond;
        molecule->bond_ptrs[(molecule->bond_no)] = bond;
        molecule->bond_no++;
        
        //lines up array of pointers to atoms pointer
        for (int i = 0; i < molecule->bond_no; i++) {
                molecule->bond_ptrs[i] = &molecule->bonds[i];
        }
    }
}

/**
 * @brief uses C's intirnal qsort function to sort the atoms and bonds within the molecules by their z-value and average z-value respectively
 * 
 * @param molecule 
 */

void molsort( molecule *molecule ) {
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(molecule->atom_ptrs[0]), compare_atoms);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(molecule->bond_ptrs[0]), bond_comp);
}

/**
 * @brief helper function for qsort for atoms
 * 
 * @param a 
 * @param b 
 * @return int 
 */
int compare_atoms (const void * a, const void * b) {
    struct atom ** atom_1 = (atom**)a;
    struct atom ** atom_2 = (atom**)b;

    return ((*atom_1)->z - (*atom_2)->z);
}

/**
 * @brief helper function for qsort for bonds
 * 
 * @param a 
 * @param b 
 * @return int 
 */
int bond_comp (const void * a, const void * b) {
    
    struct bond ** bond_1 = (bond**)a;
    struct bond ** bond_2 = (bond**)b;

    return (*bond_1)->z - (*bond_2)->z;
}

/**
 * @brief ets value in a affine matrix according to the x-axis
 * 
 * @param xform_matrix 
 * @param deg 
 */
void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    //  |   1   0           0           |    
    //  |   0   cos(theta)  -sin(theta) |
    //  |   0   sin(theta)  cos(theta)  |
    
    //row 1
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    //row 2
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(deg*PI/180);
    xform_matrix[1][2] = (-1)*sin(deg*PI/180);
    
    //row 3
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(deg*PI/180);
    xform_matrix[2][2] = cos(deg*PI/180);
}

/**
 * @brief ets value in a affine matrix according to the y-axis
 * 
 * @param xform_matrix 
 * @param deg 
 */
void yrotation( xform_matrix xform_matrix, unsigned short deg ) {
    //  |   cos(theta)      0           sin(theta)  |    
    //  |   0               1           0           |
    //  |   -sin(theta)     0           cos(theta)  |

    //row 1
    xform_matrix[0][0] = cos(deg*PI/180);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(deg*PI/180);

    //row 2
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    //row 3
    xform_matrix[2][0] = (-1)*sin(deg*PI/180);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(deg*PI/180);
}

/**
 * @brief sets value in a affine matrix according to the z-axis
 * 
 * @param xform_matrix 
 * @param deg 
 */
void zrotation( xform_matrix xform_matrix, unsigned short deg ) {
    //  |   cos(theta)   -sin(theta) 0 |    
    //  |   sin(theta)   cos(theta)  0 |
    //  |   0            0           1 |
    
    //row 1
    xform_matrix[0][0] = cos(deg*PI/180);
    xform_matrix[0][1] = (-1)*sin(deg*PI/180);
    xform_matrix[0][2] = 0;

    //row 2
    xform_matrix[1][0] = sin(deg*PI/180);
    xform_matrix[1][1] = cos(deg*PI/180);
    xform_matrix[1][2] = 0;
    
    //row 3
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

/**
 * @brief applies the transformation matrix to the atoms within the molecules
 * 
 * @param molecule 
 * @param matrix 
 */
void mol_xform( molecule *molecule, xform_matrix matrix ) {
    //check if the matrix or the molecule is empty 
    //applies the affine transformation on the atoms
    for (int i = 0; i < molecule->atom_no; i++) {
        double x = molecule->atoms[i].x;
        double y = molecule->atoms[i].y;
        double z = molecule->atoms[i].z;

        //final x-value
        molecule->atoms[i].x = (x * matrix[0][0]) + (y * matrix[0][1]) + (z * matrix[0][2]);
        //final y-value
        molecule->atoms[i].y = (x * matrix[1][0]) + (y * matrix[1][1]) + (z * matrix[1][2]);
        //final z-value
        molecule->atoms[i].z = (x * matrix[2][0]) + (y * matrix[2][1]) + (z * matrix[2][2]);
    }
    //apply the compute to all the molecules
    for (int j = 0; j < molecule->bond_no; j++) {
        compute_coords(molecule->bond_ptrs[j]);
    }
}
