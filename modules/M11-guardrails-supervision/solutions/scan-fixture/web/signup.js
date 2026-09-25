export function submit(form) {
  console.log("submitting", form);
  return fetch("/signup", { method: "POST" });
}
