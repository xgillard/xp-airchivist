import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { createPortal } from 'react-dom';
import { Alert, Box, Rating, Stack } from '@mui/material';
import FoldableList from '../foldable_list';

function ModelDetails({data, set_ranking}) {
    const params = useParams();
    const [err, set_err] = useState(null);
    const identifier = params.id;

    function on_ranking_changed(e, value) {
        set_ranking(value);
        return fetch(`${process.env.REACT_APP_API_URL}/ranking`,
            {
                method: "POST", 
                headers: {
                    "Content-Type": "application/json;encoding=utf-8",
                },
                body: JSON.stringify({
                    model: data.model,
                    identifier: identifier,
                    ranking: value,
                }),
            }
        ).then(response => {
            if (response.ok) {
                set_err(null);
            } else {
                set_err(response);
            }
        });
    }
    return (
        <Stack maxWidth="lg" sx={{width: "100%"}}>
            <Box>
                <label>{data.model}</label>
                <Rating name="size-medium"  max={5} value={data.ranking} onChange={on_ranking_changed} />
            </Box>
            <Box>
                <FoldableList title="Persons"   data={data.persons} />
                <FoldableList title="Locations" data={data.locations} />
                <FoldableList title="Dates"     data={data.dates} />
            </Box>
            {err && createPortal(<Alert severity='error' onClose={()=>{set_err(null)}}>An error happened</Alert>, document.getElementById('error')) }
        </Stack>);
}

export default ModelDetails;