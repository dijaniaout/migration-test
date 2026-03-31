// /** @odoo-module **/

import { Event } from '@customisable_workflow_report/components/event/event';
import { Component, useRef, onMounted, useState, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class Group extends Component {
    static components = { Event };
    setup() {
        super.setup();
        this.historyRef = useRef("history");
        this.orm = useService("orm");
        onWillUpdateProps((nextProps ) => {
            this.lastEvent.event = nextProps.group.events[0];
            if(nextProps.group.events.length > 1){
                this.history.showIndicator = true;
                this.oldEvents = nextProps.group.events.slice(1);
            }
            else{
                this.history.showIndicator = false;
                this.oldEvents = [];
            }
        });
        this.lastEvent = useState({event: this.props.group.events[0]});
        if (this.props.group.events.length > 1) {
            this.oldEvents = useState(this.props.group.events.slice(1));
            this.history = useState({isOpen: false, showIndicator: true});
        }
        else {
            this.oldEvents = useState([]);
            this.history = useState({isOpen: false, showIndicator: false});
        }
    }
    toggleHistory(){
        this.history.isOpen = !this.history.isOpen;
        this.history.showIndicator = !this.history.isOpen && this.oldEvents.length > 0;
    }
    async reload(){
        var events = await this.orm.searchRead(
            'customisable_workflow_report.work_doc_event',
            [
                ['res_id', '=', this.lastEvent.event.res_id],
                ['model', '=', this.lastEvent.event.model],
                ['document_id', '=', this.lastEvent.event.document_id[0]]
            ],
            ['document_id', 'type', 'create_date', 'create_user_id', 'date', 'user_id', 'reference', 'step_id', 'res_id', 
                'document_model', 'model', 'current_user_can_act', 'source_attachment', 'source_mimetype', 'source_previewable',
                'source_attachment_pdf', 'result_attachment', 'result_mimetype', 'result_previewable',
                'result_attachment_pdf', 'state', 'group_name', 'version_number'
            ],
        );
        this.lastEvent.event = events[0];
        if(events.length > 1){
            this.history.showIndicator = true;
            this.oldEvents = events.slice(1);
        }
        else{
            this.history.showIndicator = false;
            this.oldEvents = [];
        }
    }

}
Group.template = "customisable_workflow_report.GroupWidget";