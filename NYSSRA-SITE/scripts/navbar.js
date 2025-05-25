class Navbar {
    static url = window.location.host.includes('localhost')
        ? 'http://127.0.0.1:8000'
        : Globals.base_url;

    static login_token = localStorage?.getItem("nyssra_login_token");

    static async LoadExtraHTML() {
        await this.initUserData()
        document.querySelector('nav').innerHTML = await (await fetch(`/embeds/navbar.html`)).text();
        document.querySelector('footer').innerHTML = await (await fetch('/embeds/footer.html')).text();
    }

    static async getUserdata() {
        if (!this.login_token) return null;

        const res = await fetch(`${this.url}/me`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.login_token}`
            }
        });

        if (!res.ok) {
            return null;
        }

        const json = await res.json();
        return json;
    }

    static async initUserData() {
        this.user_data = await this.getUserdata();
    }

    static isAdmin() {
        return this.user_data?.admin === true;
    }
    static async loadPageFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const article = urlParams.get("article")
        if (!article || article === '' || article === null) {
            alert('Invalid article.')
            location.replace('/')
            return
        }
        const md_request = await fetch(`${Navbar.url}/pages/${article}.md`)
        const md_text = await md_request.text()
        return {'md': md_text}
    }
    static async loadPageFromName(name) {

    }
}

class Globals {
    static base_url = 'http://nyssra.pythonanywhere.com';
    static date_obj = new Date();

    static get_year() {
        return this.date_obj.getFullYear();
    }
}
