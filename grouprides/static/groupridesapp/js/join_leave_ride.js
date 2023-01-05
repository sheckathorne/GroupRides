const joinRideModal = document.getElementById('joinRideModal')
const leaveRideModal = document.getElementById('leaveRideModal')

function instantiateModal(e, modalId, formId, attributeName, action, modalAction) {
    const targetEl = document.getElementById(modalId)

    if ( modalAction === 'show' ) {
        options = {
            onShow: () => {
                const attributeValue = e.getAttribute(attributeName)
                const modalForm = targetEl.querySelector(formId)
                const actionUrl = buildActionUrl(action, attributeValue)
                modalForm.action = actionUrl
            },
        }
    } else if ( modalAction === 'hide') {
       options = {
            onHide: () => {
                const backdrop = document.querySelector('modal-backdrop')
                document.querySelector('modal-backdrop').remove();
            },
        }
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
    const modal = instantiateModal(e, 'leaveRideModal', '#leaveRideForm', 'data-bs-rideid', 'delete', 'show')
    modal.show()
}

function closeLeaveModalClick(e) {
    const modal = instantiateModal(e, 'leaveRideModal', '#leaveRideForm', 'data-bs-rideid', 'delete', 'hide')
    modal.hide()
}

function joinRideClick(e) {
    const modal = instantiateModal(e, 'joinRideModal','#joinRideForm', 'data-bs-rideid', 'create', 'show')
    modal.show()
}

function closeJoinModal(e) {
    const modal = instantiateModal(e, 'joinRideModal','#joinRideForm', 'data-bs-rideid', 'create', 'hide')
    modal.hide()
}