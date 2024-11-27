import { createBrowserRouter, Navigate, RouterProvider, useRouteError } from 'react-router-dom';

import { CssBaseline } from '@mui/material';

import {loader as load_data, LabeledData} from './components/labeled/data';

function ErrorToast() {
  const error = useRouteError();
  console.log(error);
  return <div>Oops there was an error (service is probably down)</div>;
}

function App() {
  const router = createBrowserRouter([
    {path: "*",    element: <Navigate to="0" />},
    {path: "/:id", element: <LabeledData />, errorElement: <ErrorToast />, loader: load_data}
  ]);

  return (
      <>
        <CssBaseline />
        <RouterProvider router={router} />
    </>);
  }

export default App;
