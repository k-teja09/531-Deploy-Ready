// script.js

$( "#button" ).append( "<form>Your form</form>" );

function toggleInsertForm() {
    displayType = document.getElementById("insertForm").style.display;
    if (displayType == "none") {
        document.getElementById("insertForm").style.display = "block";
    } else {
        document.getElementById("insertForm").style.display = "none";
    }
  }

  function toggleUpdateForm() {
    displayType = document.getElementById("updateForm").style.display;
    if (displayType == "none") {
        document.getElementById("updateForm").style.display = "block";
    } else {
        document.getElementById("updateForm").style.display = "none";
    }
  }

  function toggleDeleteForm() {
    displayType = document.getElementById("deleteForm").style.display;
    if (displayType == "none") {
        document.getElementById("deleteForm").style.display = "block";
    } else {
        document.getElementById("deleteForm").style.display = "none";
    }
  }
//   $(document).ready(function() {
//     $("#MyModal").modal();
//   });