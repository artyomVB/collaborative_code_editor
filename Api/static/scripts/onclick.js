let xhr = new XMLHttpRequest();
let token = null
let uid = null
let sid = null
let inSession = false
let refresh_token = null
let socket = null
let editor = null
let curr_step = 0

function goToIndex() {
    xhr.open("GET", "/login", false)
    xhr.send()
    console.log(xhr.responseText)
    var ans = JSON.parse(xhr.responseText)
    let body = document.createElement('body')
    body.innerHTML = ans.body
    document.body.replaceWith(body)
}

function updateToken() {
    xhr.open("GET", "/updateToken", false)
    xhr.setRequestHeader("Uid", uid)
    xhr.setRequestHeader("RefreshToken", refresh_token)
    xhr.send()
    var ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 0) {
        token = ans.token
        return true
    } else {
        return false
    }
}

function getSessions() {
    xhr.open("GET", "/sessions", false)
    xhr.setRequestHeader('Token', token);
    xhr.setRequestHeader("Uid", uid)
    xhr.send()
    var ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 1) {
        if (updateToken()) {
            getSessions()
        } else {
            goToIndex()
        }
    } else {
        if (inSession) {
            pos = editor.getCursor()
            socket.send(JSON.stringify({"type": "exit_session", "uid": uid, "cursor_x": pos.line, "cursor_y": pos.ch}))
            inSession = false
        }
        if (curr_step != 0) {
            curr_step = 0
        }
        let body = document.createElement('body')
        body.innerHTML = ans.body
        document.body.replaceWith(body)
    }
}

function login() {
    xhr.open("POST", "/login", false)
    var login = document.getElementById("login")
    var pass = document.getElementById("pass")
    xhr.send(JSON.stringify({"login": login.value, "password": pass.value}))
    let ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 0) {
        token = ans.token
        refresh_token = ans.refresh_token
        uid = ans.id
        getSessions()
    } else {
        alert(ans.text)
    }
}

function goToRegistration() {
    xhr.open("GET", "/signup", false)
    xhr.send()
    let ans = JSON.parse(xhr.responseText)
    let body = document.createElement('body')
    body.innerHTML = ans.body
    document.body.replaceWith(body)
}

function signUp() {
    xhr.open("POST", "/signup", false)
    var login = document.getElementById("login")
    var pass = document.getElementById("pass")
    xhr.send(JSON.stringify({"login": login.value, "password": pass.value}))
    let ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 0) {
        goToIndex()
    } else {
        let err = document.createTextNode("Choose alternative login")
        document.body.append(err)
    }
}

function getSession(id, ro) {
    xhr.open("GET", "/sessions/" + id, false)
    xhr.setRequestHeader("Token", token)
    xhr.setRequestHeader("Uid", uid)
    xhr.setRequestHeader("RO", ro.toString())
    xhr.send()
    ans = JSON.parse(xhr.responseText)
    sid = ans.sid
    if (ans.err_code == 0) {
        socket = new WebSocket("ws://localhost:" + ans.port.toString())
        socket.onopen = function () {
            socket.send(JSON.stringify({"type": "enter", "uid": uid}))
            socket.send(JSON.stringify({"type": "enter_session", "uid": uid, "sid": sid}))
        }
        inSession = true
        let body = document.createElement('body')
        body.innerHTML = ans.body
        document.body.replaceWith(body)

        handler = function() {
            socket.send(JSON.stringify({"type": "event", "uid": uid, "sid": sid, "event": arguments[1], "text": editor.getValue()}));
        }

        editor = CodeMirror.fromTextArea(document.getElementById('editor'))
        editor.replaceSelection(ans.text)
        if (!ro) {
            editor.on("change", handler)
        }

        socket.onmessage = function(event) {
            obj = JSON.parse(event.data)
            if (!ro) {
                editor.off("change", handler)
            }
            editor.replaceRange(obj.text.join("\n"), {line: obj.from.line, ch: obj.from.ch}, {line: obj.to.line, ch: obj.to.ch})
            if (!ro) {
                editor.on("change", handler)
            }
        };
    } else if (ans.err_code == 2) {
        alert(ans.text)
    } else {
        if (updateToken()) {
            getSession(id, ro)
        } else {
            goToIndex()
        }
    }
}

function createSession() {
    xhr.open("POST", "/sessions", false)
    xhr.setRequestHeader("Token", token)
    xhr.setRequestHeader("Uid", uid)
    xhr.send(JSON.stringify({"name": document.getElementById("create").value}))
    ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 1) {
        if (updateToken()) {
            createSession()
        } else {
            goToIndex()
        }
    } else {
        getSession(ans.session_id, false)
    }
}

function getShortId(long_id) {
    xhr.open("GET", "/sessions/" + long_id + "/shortid", false)
    xhr.setRequestHeader("Token", token)
    xhr.setRequestHeader("Uid", uid)
    xhr.send(null)
    ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 1) {
        if (updateToken()) {
            getShortId(long_id)
        } else {
            goToIndex()
        }
    } else {
        let p = document.getElementById('sid')
        p.innerText = ans.short_id
    }
}

function getReplay(id) {
    xhr.open("GET", "/sessions/" + id + "/replay", false)
    xhr.setRequestHeader("Token", token)
    xhr.setRequestHeader("Uid", uid)
    xhr.send(null)
    ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 1) {
        if (updateToken()) {
            getReplay(id)
        } else {
            goToIndex()
        }
    } else if (ans.err_code == 0) {
        let body = document.createElement('body')
        body.innerHTML = ans.body
        document.body.replaceWith(body)
        editor = CodeMirror.fromTextArea(document.getElementById('editor'))
    }
}

function nextStep(id) {
    xhr.open("GET", "/sessions/" + id + "/replay/" + curr_step.toString(), false)
    xhr.setRequestHeader("Token", token)
    xhr.setRequestHeader("Uid", uid)
    xhr.send(null)
    ans = JSON.parse(xhr.responseText)
    if (ans.err_code == 1) {
        if (updateToken()) {
            nextStep(id)
        } else {
            goToIndex()
        }
    } else if (ans.err_code == 0) {
        obj = JSON.parse(ans.delta)
        editor.replaceRange(obj.text.join("\n"), {line: obj.from.line, ch: obj.from.ch}, {line: obj.to.line, ch: obj.to.ch})
    }
    curr_step += 1
}