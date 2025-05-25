Navbar.LoadExtraHTML()
async function get10Posts(index) {
    var req = await fetch(`${Navbar.url}/pages_paginated`, {method: "POST", body:index})
    console.log(await req.text())
}
get10Posts()