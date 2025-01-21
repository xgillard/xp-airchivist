import Table from 'react-bootstrap/Table';
import {Accordion, AccordionSummary, AccordionDetails, Typography} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

function FoldableList({icon, title, data}) {
    return (
    <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography style={{fontWeight: "bolder"}}>{icon}</Typography>
        </AccordionSummary>
        <AccordionDetails>
            <Table striped hover>
                <tbody>
                {data.map((p,i) => <tr key={`__${title}__${i}__`}><td>{p}</td></tr>)}
                </tbody>
            </Table>
        </AccordionDetails>
    </Accordion>);
}

export default FoldableList;