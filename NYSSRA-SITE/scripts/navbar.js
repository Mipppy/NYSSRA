class Navbar {
    static url = (window.location.host.includes('localhost') ? 'http://localhost:5000' : Globals.base_url)
    static async LoadExtraHTML() {
        document.querySelector('nav').innerHTML = await (await fetch(`/embeds/navbar.html`)).text()
        document.querySelector('footer').innerHTML = await (await fetch('/embeds/footer.html')).text()
    }
    
}

class Globals {
    static base_url = 'nyssranordic.org'
    static date_obj = new Date()
    static get_year() {
        return this.date_obj.getFullYear()
    }
}