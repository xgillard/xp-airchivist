import Table from 'react-bootstrap/Table';
import {Accordion, AccordionSummary, AccordionDetails, Typography} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

function FoldableList({title, data}) {
    return (
    <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography style={{fontWeight: "bolder"}}>{title}</Typography>
        </AccordionSummary>
        <AccordionDetails>
            <Table striped hover>
                <tbody>
                {data.map(p => <tr key={`__${title}__${p}__`}><td>{p}</td></tr>)}
                </tbody>
            </Table>
        </AccordionDetails>
    </Accordion>);
}

export default FoldableList;