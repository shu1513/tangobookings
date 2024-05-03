//javacript for password confirmations in the register.html page.


document.addEventListener("DOMContentLoaded", function () {

    const editButtons = document.getElementsByClassName("editButton");
    const cancelButtons = document.getElementsByClassName("cancelButton");
    const saveButtons = document.getElementsByClassName("saveButton");

    /* activate function for edit button*/
    for (let i = 0; i < editButtons.length; i++) {
        editButtons[i].addEventListener("click", edit);
        cancelButtons[i].addEventListener("click", cancel);
        //    saveButtons[i].addEventListener("click", save);
    }

});

function edit(event) {

    const editButton = event.target;
    const container = editButton.parentElement;

    const display = container.querySelector(".display");
    const edit = container.querySelector(".edit");

    display.style.display = 'none';
    edit.style.display = 'inline';
    editButton.style.display = 'none';
}

function cancel(event) {

    const cancelButton = event.target;
    const container = cancelButton.parentElement.parentElement;
    const localEditButton = container.querySelector(".editButton");
    const display = container.querySelector(".display");
    const edit = container.querySelector(".edit");

    display.style.display = 'inline';
    edit.style.display = 'none';
    localEditButton.style.display = 'inline';
}