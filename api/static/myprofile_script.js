//javacript for password confirmations in the register.html page.


document.addEventListener("DOMContentLoaded", function () {

    const editButtons = document.getElementsByClassName("editButton")
    //const cancelButtons = document.getElementsByClassName("cancelButton")


    /* activate function for edit button*/
    for (let i = 0; i < editButtons.length; i++) {
        editButtons[i].addEventListener("click", EditMode);
    }

});

function EditMode(event) {

    /*    const emailDispaly = document.getElementById("emailDisplay")
        const emailEdit = document.getElementById("emailEdit")
        const emailInput = document.getElementById("email")
    
        const edit = document.querySelector()
    */
    const editButton = event.target;
    const container = editButton.parentElement;

    const display = container.querySelector(".display");
    const edit = container.querySelector(".edit");

    display.style.display = 'none';
    edit.style.display = 'block';
    editButton.style.display = 'none';
}