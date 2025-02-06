import { createBrowserRouter, Navigate, RouterProvider, useRouteError } from 'react-router-dom';

import { CssBaseline } from '@mui/material';

import {loader as load_data, LabeledData} from './components/labeled/data';
import NamePicker from './components/pick_a_name';
import { useState } from 'react';

function ErrorToast() {
  const error = useRouteError();
  console.log(error);
  return (
    <>
      <div>Oops there was an error (service is probably down)</div>
      <div>{import.meta.env.VITE_API_URL}</div>
    </>);
}

function App() {
  const router = createBrowserRouter([
    {path: "/",                   element: <Navigate to="/pick"  />},
    {path: "/pick",               element: <NamePicker  />},
    {path: "/label/:usrname/:id", element: <LabeledData />, errorElement: <ErrorToast />, loader: load_data}
  ]);

  return (
      <>
        <CssBaseline />
        <RouterProvider router={router} />
    </>);
  }

export default App;
