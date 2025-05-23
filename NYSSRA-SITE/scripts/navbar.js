class Navbar {
    static url = (window.location.host.includes('localhost') ? 'http://127.0.0.1:8000' : Globals.base_url)
    static async LoadExtraHTML() {
        document.querySelector('nav').innerHTML = await (await fetch(`/embeds/navbar.html`)).text()
        document.querySelector('footer').innerHTML = await (await fetch('/embeds/footer.html')).text()
    }
    
}

class Globals {
    static base_url = 'http://nyssra.pythonanywhere.com'
    static date_obj = new Date()
    static get_year() {
        return this.date_obj.getFullYear()
    }
}