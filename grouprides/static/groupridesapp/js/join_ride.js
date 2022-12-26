const joinRideModal = document.getElementById('joinRideModal')

joinRideModal.addEventListener('show.bs.modal', e => {
    const button = e.relatedTarget
    const occurenceid = button.getAttribute('data-bs-occurenceid')
    const modalForm = exampleModal.getElementById('joinRideForm')
    modalForm.action = `/rides/registration/{occurenceid}/create/`
})