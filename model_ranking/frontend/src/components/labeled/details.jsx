import { useState } from "react";
import { Box, Container, Tab, Tabs } from "@mui/material";
import ModelDetails from "./details_model";
import TranscriptionDetails from "./details_transcription";

export function LabeledDetails({data, set_data}) {
    const [tab, set_tab]   = useState("text");

    function setter(k) {
        return function(x) {
            set_data(d => ({
                ...d, 
                docdata: {
                    ...d.docdata, 
                    [k]: {
                        ...d.docdata[k],
                        ranking: x
                    }
                }
            }))
        }
    };

    return (<>
        <Box sx={{display: "flex", alignItems: "center", justifyContent: "center"}}>
            <Tabs variant="scrollable" value={tab} onChange={(_e,v) => set_tab(v)}>
                <Tab value="text" label="Text" />
                { Object.entries(data.docdata).map(([k,_v]) => <Tab key={`tab-${k}`} value={k} label={k} />) }
            </Tabs>
        </Box>
        <Container>
            {(tab === "text") && <TranscriptionDetails text={data.text} /> }
            {(tab !== "text") && <ModelDetails key={tab} data={data.docdata[tab]} set_ranking={setter(tab)} /> }
        </Container>
        </>);
};

export default LabeledDetails;