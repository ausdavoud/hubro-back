async function connect_to_ws() {
  const roomName = JSON.parse(document.getElementById("room-name").textContent);
  let uuid = "";
  const response = await fetch(
    "http://127.0.0.1:8000/auth_for_ws_connection/",
    {
      headers: {
        Authorization:
          "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI3MTczMzcwLCJpYXQiOjE3MjcxNzEzMDksImp0aSI6IjE0NWYxNGZjNmQ2ZTQyMWVhN2I0YmI1YzRjM2QxNjYwIiwidXNlcl9pZCI6MX0.kJhNbjX7HNElHs7XgAKDr2W5GGxkxP6G3zxCBkYkZ-c",
      },
    }
  );
  const response_json = await response.json();
  uuid = response_json.uuid;

  const chatSocket = new WebSocket(
    "ws://" +
      window.location.host +
      "/ws/chat/" +
      roomName +
      "/" +
      "?uuid=" +
      uuid
  );

  chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    document.querySelector("#chat-log").value += data.response.message + "\n";
    if (data.response.factory) {
      document.querySelector("#chat-log").value +=
        "\nINFO: " + JSON.stringify(data.response.factory);
    }
  };

  chatSocket.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
  };

  document.querySelector("#chat-message-input").focus();
  document.querySelector("#chat-message-input").onkeyup = function (e) {
    if (e.key === "Enter") {
      // enter, return
      document.querySelector("#chat-message-submit").click();
    }
  };

  document.querySelector("#chat-message-submit").onclick = function (e) {
    const messageInputDom = document.querySelector("#chat-message-input");
    const message = messageInputDom.value;
    const [action, name, price] = message.split(" ");
    chatSocket.send(
      JSON.stringify({
        action: action,
        data: {
          name: name,
          price: price,
        },
      })
    );
    messageInputDom.value = "";
  };
}

connect_to_ws();
