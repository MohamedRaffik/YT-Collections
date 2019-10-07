import React, { useEffect, useState } from 'react';
import './Subscriptions.scss';

const Channel = () => {
    return (
        <div className="channel-view">
            <div className="channel-img">
                <img src="https://picsum.photos/200" />
                <button>X</button>
            </div>
            <div className="channel-info">
                <h3>Channel Name</h3>
                <p>Subscribed on 01/01/01</p>
            </div>
        </div>
    )
}

const Subscription = () => {
    const [Subscriptions, setSubscriptions] = useState([]);
    const [Page, setPage] = useState(0);
    const [LoadNextPage, setLoadNextPage] = useState(true);
    const [LoadingSubscriptions, setLoadingSubscriptions] = useState(true);

    const getSubscriptions = (page) => {
        if (!LoadNextPage) return;
        fetch('/api/subscriptions/page/0')
            .then(response => {
                if (response.status === 202) {
                    window.requestInterval = window.requestInterval ? window.requestInterval : setInterval(() => getSubscriptions(0), 5000);
                    return;
                }
                response.json().then(data => {
                    clearInterval(window.requestInterval);
                    console.log(data);
                    setLoadingSubscriptions(false);
                    setSubscriptions(data.subscriptions);
                    if (Page == data.total_pages) setLoadNextPage(false);
                })
                .catch(err => console.error(err));
            })
            .catch(err => console.error(err));
    }

    useEffect(() => { 
        getSubscriptions(0);
    }, []);
    // useEffect(() => { if (Page != 0) getSubscriptions(Page) } , [Page])

    return (
        <div className="content">
            <div className="sub-search">
                <input placeholder="Search Subscriptions" />
            </div>
            <h3 style={{textAlign: 'right', color: 'red'}}>Subscription Count: 700</h3>
            <div className="sub-view">
                { Array(20).fill(0).map((val, index) => <Channel key={`index${index}`} />) }
            </div>
        </div>
    );
};

export default Subscription;