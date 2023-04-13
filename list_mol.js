
/* javascript to accompany molecules.html */
$(document).ready(function () {
    $.ajax({
        url: '/list_mol', // the URL to your Flask route that returns the molecules
        type: 'GET',
        dataType: 'json', 
        success: function (data, status, xhr) {
            var molecule_list = $('#molecule-list'); // get the molecule-list container
            molecule_list.empty(); // empty current elements
            if (xhr.status === 204) {
                console.log("database_empty")
                var empty_bar = $('<div class="empty-bar"></div>').css('white-space', 'pre-line').text("+ Upload Molecule");
                empty_bar.on('click', function() {
                    window.location.href = 'upload_page.html';
                });
                molecule_list.append(empty_bar);
            }
            else {
                var molecules = data; // convert the response to a JavaScript object
                console.log("succeeded");
                // loop through the molecules and add them to the molecule_list container
                for (var i = 0; i < molecules.length; i++) {
                    var molecule = molecules[i];

                    // create a new molecule bar element
                    var molecule_bar = $('<div class="molecule-bar"></div>');

                    // set the molecule name as the bar's text
                    molecule_bar.append($('<span class="molecule-name"></span>').text(molecule.name));

                    // wrap the atom and bond counts in a separate container
                    var molecule_info = $('<div class="molecule-info"></div>');
                    molecule_info.append($('<span class="molecule-atoms"></span>').text('Atoms: ' + molecule.atom_count));
                    molecule_info.append($('<span class="molecule-bonds"></span>').text('Bonds: ' + molecule.bond_count));
                    molecule_bar.append(molecule_info);

                    // add a click event to the molecule_bar element that calls the process_molecule function with the molecule name
                    molecule_bar.on('click', function () {
                        var molecule_name = $(this).find('.molecule-name').text();
                        process_molecule(molecule_name);
                    });

                    // add the molecule_bar element to the page
                    molecule_list.append(molecule_bar);
                }
            }
        },
        error: function(xhr, textStatus, errorThrown){
            console.log(xhr.status);
            console.log(errorThrown);
        }
    });

    function process_molecule(molecule_name) {
        $.ajax({
          url: '/viewer', // the URL to your Flask route that processes the molecule
          type: 'POST',
          data: {'name': molecule_name},
          success: function (response) {
            console.log(response);
            window.location.href = '/viewer.html'; // redirect to viewer.html
          },
          error: function (xhr, textStatus, errorThrown) {
            console.log(xhr.status);
            console.log(errorThrown);
          }
        });
    }
});