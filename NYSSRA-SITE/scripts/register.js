(async () => {
    await Navbar.LoadExtraHTML()
    if (Navbar.user_data !== null) {
        alert("You are already logged in!")
        window.location.href = '/'
    }
})()

async function loginUser(isRegister, username, password) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch(`${Navbar.url}/${isRegister ? 'register' : 'login'}`, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    if (response.ok && data.status === 'success') {
      return { success: true, message: data.message, token: data.token };
    } else {
      return { success: false, message: data.message || (isRegister ? 'Registration failed' : 'Login failed') };
    }
  } catch (error) {
    return { success: false, message: 'Network error or server unavailable' };
  }
}

document.getElementById('registerForm').addEventListener('submit', async (ev) => {
  ev.preventDefault();

  const usernameInput = document.getElementById('registerUsername');
  const passwordInput = document.getElementById('registerPassword');
  const registerButton = document.getElementById('registerButton');

  let valid = true;

  if (!usernameInput.value.trim()) {
    usernameInput.classList.add('is-invalid');
    valid = false;
  } else {
    usernameInput.classList.remove('is-invalid');
  }

  if (!passwordInput.value) {
    passwordInput.classList.add('is-invalid');
    valid = false;
  } else {
    passwordInput.classList.remove('is-invalid');
  }

  if (!valid) return;

  if (window.isbot) {
    alert('Successfully created account!\nWelcome to NYSSRA!');
    return;
  }

  const result = await loginUser(true, usernameInput.value.trim(), passwordInput.value);

  if (result.success) {
    alert('Account created successfully! Welcome to NYSSRA!');
    usernameInput.value = '';
    passwordInput.value = '';
    usernameInput.disabled = true;
    passwordInput.disabled = true;
    registerButton.disabled = true;
  } else {
    alert(`Error: ${result.message}`);
  }
});

document.getElementById('loginForm').addEventListener('submit', async (ev) => {
  ev.preventDefault();

  const usernameInput = document.getElementById('loginUsername');
  const passwordInput = document.getElementById('loginPassword');
  const loginButton = document.getElementById('loginButton');

  let valid = true;

  if (!usernameInput.value.trim()) {
    usernameInput.classList.add('is-invalid');
    valid = false;
  } else {
    usernameInput.classList.remove('is-invalid');
  }

  if (!passwordInput.value) {
    passwordInput.classList.add('is-invalid');
    valid = false;
  } else {
    passwordInput.classList.remove('is-invalid');
  }

  if (!valid) return;

  if (window.isbot) {
    alert('Login successful! Welcome back!');
    return;
  }

  const result = await loginUser(false, usernameInput.value.trim(), passwordInput.value);

  if (result.success) {
    alert('Login successful! Welcome back!');
    usernameInput.value = '';
    passwordInput.value = '';
    localStorage.setItem('nyssra_login_token', result.token)
  } else {
    alert(`Error: ${result.message}`);
  }
});