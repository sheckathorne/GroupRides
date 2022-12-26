const joinRideModal = document.getElementById('joinRideModal')
const leaveRideModal = document.getElementById('leaveRideModal')

if ( joinRideModal ) {
    joinRideModal.addEventListener('show.bs.modal', e => {
        const button = e.relatedTarget
        const occurenceid = button.getAttribute('data-bs-occurenceid')
        const modalForm = joinRideModal.querySelector('#joinRideForm')
        const actionUrl = `/rides/registration/${occurenceid}/create/`

        modalForm.action = actionUrl
    })
}

if ( leaveRideModal ) {
    leaveRideModal.addEventListener('show.bs.modal', e => {
        const button = e.relatedTarget
        const rideId = button.getAttribute('data-bs-rideId')
        const modalForm = leaveRideModal.querySelector('#leaveRideForm')
        const actionUrl = `/rides/registration/${rideId}/delete/`

        modalForm.action = actionUrl
    })
}
