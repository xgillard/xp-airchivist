import CheckIcon from '@mui/icons-material/Check';
import { Box, Button, Card, CardActions, CardContent, CardHeader, TextField, Typography } from "@mui/material";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function NamePicker() {
    const navigate = useNavigate();
    const [usrname, set_usrname] = useState();
    return (
        <Box sx={{display: "flex", width: "100%", height: "100vh", backgroundColor: "lightblue", alignItems: "center", justifyContent: "center"}}>
        <Card sx={{maxWidth: 500, maxHeight: 300}}>
            <CardContent>
                <Typography variant='h5' component="div" sx={{padding: ".5em"}}>Please Pick a Name</Typography>
                <TextField label="Name" variant="outlined" sx={{width: "100%", marginBottom: "1em"}} onChange={(e) => set_usrname(e.target.value)}/>
                <Typography color='text.secondary' component="div" sx={{marginBottom: "1em"}}>
                    Initials / Pseudo / ... this is not meant to identify you.
                    It is only meant to avoid overwriting your colleague's work.
                </Typography>
            </CardContent>
            <CardActions>
                <Button onClick={() => navigate(`/label/${usrname}/0`)}> Let's Go ! <CheckIcon /></Button>
            </CardActions>
        </Card>
        </Box>
    );
}