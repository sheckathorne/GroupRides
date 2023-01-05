const joinRideModal = document.getElementById('joinRideModal')
const leaveRideModal = document.getElementById('leaveRideModal')

function instantiateModal(e, modalId, formId, attributeName, action) {
    const targetEl = document.getElementById(modalId)

    const options = {
        onHide: () => {
            const backdrop = document.querySelector('[modal-backdrop]')
            document.querySelector('[modal-backdrop]').remove();
        },
        onShow: () => {
            const attributeValue = e.getAttribute(attributeName)
            const modalForm = targetEl.querySelector(formId)
            const actionUrl = buildActionUrl(action, attributeValue)
            modalForm.action = actionUrl
        },
    }

    const modal = new Modal(targetEl, options)

    return modal
}

function buildActionUrl(action, id) {
    if ( action === 'delete' ) {
        return `/rides/registration/${id}/delete/`
    } else if ( action === 'create' ) {
        return `/rides/registration/${id}/create/`
    } else {
        return ''
    }
}

function leaveRideClick(e) {
    const modal = instantiateModal(e, 'leaveRideModal', '#leaveRideForm', 'data-bs-rideid', 'delete')
    modal.show()
}

function closeLeaveModalClick(e) {
    const modal = instantiateModal(e, 'leaveRideModal', '#leaveRideForm', 'data-bs-rideid', 'delete')
    modal.hide()
}

function joinRideClick(e) {
    const modal = instantiateModal(e, 'joinRideModal','joinRideForm', 'data-bs-rideid', 'create')
    modal.show()
}