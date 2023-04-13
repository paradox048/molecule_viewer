/* javascript to accompany jquery.html */

$(document).ready( 
  /* this defines a function that gets called after the document is in memory */
  function()
  {
	function updateList() {
		$.ajax({
		  url: "/display_element_list",
		  dataType: "json",
		  success: function (data) {
			var list = $("#myList");
			if (Object.keys(data).length == 0) {
			  list.empty(); // Clear the current list
			  var item = $("<li>").text("+ Element").click(function() {
				$("#toggle_add_remove").click();
			  })
			  list.append(item);
			} else {
			  list.empty(); // Clear the current list
			  Object.keys(data).forEach(function (key) {
				var item = $("<li>").text(data[key]).click(function () {
				  var confirmed = confirm("Are you sure you want to delete this element?");
				  if (confirmed) {
					var elemName = $(this).text();
					console.log("Deleting element: " + elemName);

					$.post("/form_handler.html", {
					  operation: "remove",
					  reCode: elemName,
					})
				  }
				})
				list.append(item);
			  })
			}
		  }
		}) 
	  }

      // Update the list every 5 seconds
      setInterval(updateList, 1000);
	  
    /* add a click handler for our button */
    $("#toggle_add_remove").change(
      function()
      {	
		this.value = !this.value;
		if (this.value == true) {
			$("#remove_e_div").toggle();  /* show element num */
			$("#add_e_div").toggle();  /* show element num */
			this.value = false;
		} else { //if value is ON
			$("#remove_e_divs").toggle();  /* show element num */
			$("#add_e_div").toggle();  /* show element num */
			this.value = true;
		}
      }
    );

	$("#add_element").click(
		function () 
		{
			/* ajax post */
			$.post("/form_handler.html", {
				/* pass a JavaScript dictionary */
				operation: "add",
				eNumber: $("#element_num").val(),
				eCode: $("#element_code").val(),
				eName: $("#element_name").val(),
				col1: $("#c_1").val(),
				col2: $("#c_2").val(),
				col3: $("#c_3").val(),
				rad: $("#e_rad").val()
			}).done (function (data) {
				console.log(data);
				alert("Submission succeeded!");
			}).fail(function (xhr, status, error) {
				console.log(xhr)
				alert("Submission failed!");
			});
    	});
  });
