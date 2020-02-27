import dash_bootstrap_components as dbc

def Navbar():
    navbar = dbc.Nav(
            [
                dbc.NavItem(
                    dbc.NavLink(
                    "Internal link",
                    href="/l/components/nav"
                    )
                ),
                
                dbc.NavItem(
                    dbc.NavLink(
                    "External link",
                    href="https://github.com"
                    )
                ),
                
                dbc.NavItem(
                    dbc.NavLink(
                        "External relative",
                        href="/l/components/nav",
                        external_link=True,
                    )
                )
            ],
            pills = True,
        )

    return navbar