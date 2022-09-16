// on click id "install-button"
document.getElementById("install-button").addEventListener("click", function () {
  const curl = document.getElementById("curl").checked ? "1" : "0";
  const angle = document.getElementById("angle").checked ? "1" : "0";
  const wide = document.getElementById("wide").checked ? "1" : "0";
  const symbol = document.getElementById("symbol").checked ? "1" : "0";
  const extend = document.getElementById("extend").checked ? "1" : "0";

  url = `karabiner://karabiner/assets/complex_modifications/import?url=${curl}${angle}${wide}${symbol}${extend}.json`;
  window.location.href = url;

  let description = "Colemak ";
  if (curl === "1") {
    description += "C";
  }
  if (angle === "1") {
    description += "A";
  }
  if (wide === "1") {
    description += "W";
  }
  if (symbol === "1") {
    description += "S";
  }
  if (description === "Colemak ") {
    description = "Vanilla Colemak";
  }
  if (extend === "1") {
    description += " with Extend";
  }

  document.getElementById("layout-placeholder").innerText = description;
  document.getElementById("code").innerText = url;
  document.getElementById("copy-button").innerText = "Copy";

  document.getElementById("create-layout").classList.add("hidden");
  document.getElementById("layout-created").classList.remove("hidden");
});

document.getElementById("back-button").addEventListener("click", function () {
  document.getElementById("create-layout").classList.remove("hidden");
  document.getElementById("layout-created").classList.add("hidden");
});

document.getElementById("copy-button").addEventListener("click", function () {
  const textToCopy = document.getElementById("code").innerText;
  navigator.clipboard.writeText(textToCopy);

  document.getElementById("copy-button").innerText = "Copied!";
});