let socket = new WebSocket("ws://localhost:8080");
console.log("here")

handler = function(){
    socket.send(JSON.stringify(arguments[1]));
}

let editor = CodeMirror.fromTextArea(document.getElementById('editor'))
editor.on("change", handler)

socket.onopen = function(e) {
    socket.send("session_id");
};

socket.onmessage = function(event) {
    obj = JSON.parse(event.data)
    editor.off("change", handler)
    editor.replaceRange(obj.text.join("\n"), {line: obj.from.line, ch: obj.from.ch}, {line: obj.to.line, ch: obj.to.ch})
    editor.on("change", handler)
};
