import { useEffect, useState } from 'react';
import { useLoaderData, useNavigate } from "react-router-dom";
import { AppBar, Badge, Box, ButtonGroup, IconButton, Toolbar, Typography } from '@mui/material';

import StarsIcon from '@mui/icons-material/Stars';
import ArrowBack from '@mui/icons-material/ArrowBackIos';
import ArrowFwd  from '@mui/icons-material/ArrowForwardIos';

import LabeledDetails from "./details";

// FIXME
const LIMIT = 419;

export function LabeledData() {
    const loaded = useLoaderData();
    const [data, set_data] = useState(loaded);
    const navigate = useNavigate();

    useEffect(function () {
        set_data(loaded);
    }, [loaded]);

    function backwards(){
        let x = data.identifier - 1;
        if (x < 0) {
            x = 0;
        }
        return navigate(`/${x}`);
    }
    function forwards(){
        let x = data.identifier + 1;
        if (x >= LIMIT) {
            x = 0;
        }
        return navigate(`/${x}`);
    }

    let nb_tasks = 0;
    if (data) {
        for (const v of Object.values(data.docdata)) {
            if (!v.ranking) { nb_tasks += 1;} 
        }
    }

    return (
        <>
        { (data) && 
            <>
            <AppBar sx={{alignItems: "center"}}>
                <Box maxWidth="lg" sx={{display: "inline-block", width: "100%"}} >
                    <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center'}} >
                        <Box padding="1em">
                            <Typography variant="h6" sx={{ verticalAlign: "middle" }}>
                                <Badge badgeContent={nb_tasks} color="warning">
                                    <StarsIcon fontSize="large"/> Model Ranking
                                </Badge>
                            </Typography>
                        </Box>
                        <Box>
                            <Typography>#{data.identifier}</Typography>
                        </Box>
                        <Box>
                            <ButtonGroup sx={{right: 0, marginLeft: "auto"}}>
                                <IconButton size="large"  onClick={backwards}><ArrowBack htmlColor='white'/></IconButton>
                                <IconButton size="large"  onClick={forwards} ><ArrowFwd  htmlColor='white'/></IconButton>
                            </ButtonGroup>
                        </Box>
                    </Toolbar>
                </Box>
            </AppBar>
            <Box padding="1.5em">
                <Toolbar />
                <LabeledDetails data={data} set_data={set_data} />
            </Box>
            </>
        }
        </>);
}

export async function loader({params}) {
    const identifier = params.id;
    return fetch(`${import.meta.env.VITE_API_URL}/by_id/${identifier}`,
        {
            method: "GET",
		headers: {
			"Referrer-Policy": "origin-when-cross-origin"
		}
        }
    ).then(response => {
        if (!response.ok) {
            throw new Error("Bad response");
        } else {
            return response.json();
        }
    });
}

export default LabeledData;
