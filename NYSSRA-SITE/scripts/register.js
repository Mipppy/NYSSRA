Navbar.LoadExtraHTML()
async function registerUser(username, password) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch('/register', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    if (response.ok && data.status === 'success') {
      return { success: true, message: data.message };
    } else {
      return { success: false, message: data.message || 'Registration failed' };
    }
  } catch (error) {
    return { success: false, message: 'Network error or server unavailable' };
  }
}

document.getElementById('registerForm').addEventListener("submit", async (ev) => {
  ev.preventDefault();  
  
  if (window.isbot) {
    // get fucked
    alert('Successfully created account!\nWelcome to NYSSRA!');
    return;
  }

  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById("password");
  const registerButton = document.getElementById('registerButton')

  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  if (!username || !password) {
    alert('Please fill in both username and password.');
    return;
  }

  const result = await registerUser(username, password);

  if (result.success) {
    alert('Account created successfully! Welcome to NYSSRA!');
    usernameInput.value = '';
    passwordInput.value = '';
    usernameInput.disabled = true
    passwordInput.disabled = true
    registerButton.disabled = true
  } else {
    alert(`Error: ${result.message}`);
  }
});
