import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Link, Switch } from 'react-router-dom';
import './App.scss';
import { Subscriptions } from './components';
import YTLogo from './images/YouTube_full-color_icon_(2017).svg';
import Settings_Logo from './images/settings-32.ico'

const NavOptions = (props) => {
    const { ShowAccount, LoginAction, UserName } = props;
    return [
        <Link to='/subscriptions' key="subs">Subscriptions</Link>,
        <a key="colls">Collections</a>,
        <a key="playlists">Playlists</a>,
        <a key="vid">Video Player</a>,
        ShowAccount ? <AccountView key="account" UserName={UserName} LoginAction={LoginAction} /> : null
    ]
};

const AccountView = (props) => {
    const { UserName, LoginAction } = props;
    return UserName ? 
        <a className="nav-name">{UserName}</a>
        :
        <a className="nav-name" onClick={LoginAction}>Sign In</a>
    ;
};

const MobileNavBar = (props) => {
    const { SetDropdown, ShowDropdown, LoginAction, UserName, Size } = props;

    const NavButton = () => <a onClick={SetDropdown}>&#9776;</a>;

    const NavDropDown = () => {
        return (
            <div className="nav-dropdown" style={{display: ShowDropdown ? 'flex' : 'none'}}>
                <NavOptions ShowAccount={Size === 'small'} UserName={UserName} LoginAction={LoginAction} />
            </div>
        )
    };

    return (
        <div className={Size === 'small' ? "small-nav" : "med-nav"}>
            <div className="nav-bar">
                <NavButton />
                <a className="title">
                    <img src={YTLogo} />
                    <h4>YT Collections</h4>
                </a>
                { Size === 'medium' ? <AccountView UserName={UserName} LoginAction={LoginAction} /> : null }
            </div>
            <NavDropDown />
        </div>
    )
}

const NavBar = (props) => {
    const { LoginAction, UserName } = props;
    return (
        <div className="large-nav">
            <a className="title">
                <img src={YTLogo} />
                <h4>YT Collections</h4>
            </a>
            <NavOptions ShowAccount={true} LoginAction={LoginAction} UserName={UserName} />
        </div>
    );
}

const App = () => {
    const [UserName, setUserName] = useState('');
    const [RedirectURL, setRedirectURL] = useState('');
    const [ShowNavMenu, setShowNavMenu] = useState(false);

    const OAuthLogin = () => window.location = RedirectURL;

    useEffect(() => {
        fetch('/api/auth/login')
            .then(response => response.json())
            .then(data => data.redirect ? setRedirectURL(data.redirect_url) : setUserName(data.username))
            .catch(err => console.log(err));
    }, []);

    return (
        <Router>
            <div>
                <nav>
                    <MobileNavBar Size={'small'} ShowDropdown={ShowNavMenu} SetDropdown={() => setShowNavMenu(!ShowNavMenu)} LoginAction={OAuthLogin} UserName={UserName} />
                    <MobileNavBar Size={'medium'} ShowDropdown={ShowNavMenu} SetDropdown={() => setShowNavMenu(!ShowNavMenu)} LoginAction={OAuthLogin} UserName={UserName} />
                    <NavBar LoginAction={OAuthLogin} UserName={UserName} />
                </nav>
                <Switch>
                    <Route path='/' component={Subscriptions}></Route>
                    <Route path='/subscriptions' component={Subscriptions}></Route>
                </Switch>
            </div>
        </Router>
    );
};

export default App;