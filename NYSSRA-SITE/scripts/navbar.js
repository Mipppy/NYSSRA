class Navbar {
    static url = window.location.host.includes('localhost')
        ? 'http://127.0.0.1:8000'
        : Globals.base_url;

    static login_token = localStorage?.getItem("nyssra_login_token");
    static showdownParameters = {
        tables: true,
        openLinksInNewWindow: true,
        extensions: [function () {
            return [{
                type: 'output',
                filter: function (text) {
                    return text.replace(/<table(\s*[^>]*)>/g, '<table$1 class="table table-striped table-bordered">');
                }
            }];
        }]
    }


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
        if (this.user_data?.admin === false) {
            document.querySelectorAll('#admin_only').forEach(ele => {
                ele.remove()
            })
        }
    }

    static isAdmin() {
        return this.user_data?.admin === true;
    }
    static parsePageData(dataText) {
        const lines = dataText.trim().split('\n');
        const date = new Date(lines[1]) || null
        return {
            tags: (lines[0] || '').split(',').map(s => s.trim()).filter(Boolean),
            date: `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}` || null,
            author: lines[2] || null,
            postName: lines[3] || null,
            isEvent: lines[4]?.toLowerCase().trim() === 'true',
            eventDate: lines[5] || null,
            numOfImages: parseInt(lines[6]) || 0
        };
    }

    static async loadPageFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const article = urlParams.get("article");

        if (!article) {
            alert('Invalid article.');
            location.replace('/');
            return;
        }

        const md_request = await fetch(`${Navbar.url}/pages/${article}.md`);
        const md_text = await md_request.text();

        const article_req = await fetch(`${Navbar.url}/page_data/${article}.txt`);
        const article_data = await article_req.text();
        const parsed_data = this.parsePageData(article_data);

        return { md: md_text, pd: parsed_data, article: article };
    }

    static async loadPageFromName(name) {
        let new_name = this.replaceLast(name, '.md', '');

        const md_request = await fetch(`${Navbar.url}/pages/${new_name}.md`);
        const md_text = await md_request.text();

        const article_req = await fetch(`${Navbar.url}/page_data/${new_name}.txt`);
        const article_data = await article_req.text();
        const parsed_data = this.parsePageData(article_data);

        return { md: md_text, pd: parsed_data, article: new_name };
    }
    static replaceLast(str, search, replace) {
        const index = str.lastIndexOf(search);
        if (index === -1) return str;
        return str.substring(0, index) + replace + str.substring(index + search.length);
    }
    static async loadCalendar(ele) {
        const req = await fetch("/embeds/calender.html")
        const htmlData = await req.text()
        ele.innerHTML = htmlData
        return htmlData
    }
    static async loadAllEvents() {
        const req = await fetch(`${Navbar.url}/all_events`)
        const json = await req.json()
        return json
    }

    static turnToCorrectDate(dateStr) {
        const d = new Date(dateStr);
        const day = d.getDate();
        const month = d.getMonth() + 1;
        const year = d.getFullYear();

        let hour = d.getHours();
        const minute = d.getMinutes().toString().padStart(2, '0');
        const ampm = hour >= 12 ? 'PM' : 'AM';

        hour = hour % 12;
        if (hour === 0) hour = 12;

        return `${day}/${month}/${year} ${hour}:${minute} ${ampm}`;
    }

    static generateTagFormat(tag) {
        return `
    <a href="/search.html?tags=${tag}" style="
        display: inline-block;
        background-color: #d3d3d3;
        color: black;
        border-radius: 12px;
        padding: 2px 10px;
        margin: 2px 4px 2px 0;
        font-size: 0.9em;
        cursor: pointer;
        white-space: nowrap;
        text-decoration: none;">
        ${tag}
    </a>`
    }
}

class Globals {
    static base_url = 'http://nyssra.pythonanywhere.com';
    static date_obj = new Date();

    static get_year() {
        return this.date_obj.getFullYear();
    }
}
