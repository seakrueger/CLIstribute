export function submit(form_data) {
    return fetch(`./api/submit?data=${form_data}`)
        .then((r) => r.json())
        .then((data) => {
            return data
        })
}

export function getCommands() {
    return fetch(`./api/commands`)
        .then((r) => r.json())
        .then((data) => {
            return data
        })
}

export function getWorkers() {
    return fetch(`./api/workers`)
        .then((r) => r.json())
        .then((data) => {
            return data
        })
}

export function getLogs() {
    return fetch(`./api/logs`)
        .then((r) => r.json())
        .then((data) => {
            return data
        })
}
