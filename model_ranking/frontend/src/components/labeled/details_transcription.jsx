import { Box, Divider, Paper, Typography } from "@mui/material";

function TranscriptionDetails({text}) {
    return (
    <Paper>
        <Box padding={3}>
            <Typography variant="h5">Transcription</Typography>
            <Divider />
            <Box mt={3}>
                <Typography>{text}</Typography>
            </Box>
        </Box>
    </Paper>);
}

export default TranscriptionDetails;