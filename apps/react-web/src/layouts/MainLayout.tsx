import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from '../components/Header';
import {Footer} from "../components/Footer.tsx";

export const MainLayout: React.FC = () => {
    return (
        <div className="min-h-screen flex flex-col font-sans">
            <Header />
            <main className="flex-1 bg-gray-50">
                <Outlet />
            </main>
            <Footer />
        </div>
    );
};