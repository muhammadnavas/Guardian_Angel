import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
    const [scrolled, setScrolled] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 40);
        window.addEventListener('scroll', onScroll);
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    useEffect(() => setMenuOpen(false), [location]);

    const linkClass = (path) =>
        `flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-full transition-all duration-150 ${location.pathname === path
            ? 'bg-primary-light/12 text-primary-light'
            : 'text-gray-400 hover:text-white hover:bg-white/[0.04]'
        }`;

    return (
        <nav
            className={`fixed top-0 inset-x-0 z-50 transition-all duration-250 ${scrolled
                    ? 'bg-[#0a0e1a]/85 backdrop-blur-xl border-b border-white/[0.08] py-2'
                    : 'bg-transparent py-4'
                }`}
        >
            <div className="max-w-[1200px] mx-auto px-6 flex items-center justify-between">
                <Link to="/" className="flex items-center gap-2 no-underline">
                    <span className="text-3xl drop-shadow-[0_0_8px_rgba(99,102,241,0.25)]">🛡️</span>
                    <span className="font-heading text-xl font-bold bg-gradient-to-r from-white to-primary-light bg-clip-text text-transparent">
                        Guardian Angel
                    </span>
                </Link>

                <button
                    className="md:hidden flex flex-col gap-[5px] p-2 bg-transparent"
                    onClick={() => setMenuOpen(!menuOpen)}
                    aria-label="Toggle menu"
                >
                    <span className="block w-6 h-0.5 bg-white rounded"></span>
                    <span className="block w-6 h-0.5 bg-white rounded"></span>
                    <span className="block w-6 h-0.5 bg-white rounded"></span>
                </button>

                <ul
                    className={`list-none flex items-center gap-1 
          max-md:fixed max-md:top-0 max-md:h-screen max-md:w-[280px] max-md:flex-col max-md:items-start 
          max-md:bg-surface max-md:border-l max-md:border-white/[0.08] max-md:pt-16 max-md:px-6 max-md:gap-2
          max-md:transition-all max-md:duration-400
          ${menuOpen ? 'max-md:right-0' : 'max-md:right-[-100%]'}`}
                >
                    <li><Link to="/" className={linkClass('/')}>🏠 Home</Link></li>
                    <li><Link to="/scan" className={linkClass('/scan')}>🔍 Scan</Link></li>
                    <li><Link to="/history" className={linkClass('/history')}>📊 History</Link></li>
                    <li><Link to="/about" className={linkClass('/about')}>ℹ️ About</Link></li>
                    <li className="ml-2 max-md:ml-0 max-md:w-full">
                        <Link
                            to="/scan"
                            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-full bg-gradient-to-br from-primary to-primary-light text-white btn-glow hover:-translate-y-0.5 transition-all duration-250 max-md:w-full"
                        >
                            Start Scan
                        </Link>
                    </li>
                </ul>
            </div>
        </nav>
    );
}
