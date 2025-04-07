import React from 'react';

const Layout: React.FC = ({ children }) => {
    return (
        <div>
            <header>
                <h1>My Next.js Microservices App</h1>
            </header>
            <main>{children}</main>
            <footer>
                <p>© 2023 My Next.js Microservices App</p>
            </footer>
        </div>
    );
};

export default Layout;