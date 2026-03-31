// /** @odoo-module **/
import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Group } from '@customisable_workflow_report/components/group/group';
import { GroupTitle } from '@customisable_workflow_report/components/group_title/group_title';
import { useRecordObserver } from "@web/model/relational_model/utils";

export class DocumentEventWidget extends Component {
    static components = { GroupTitle , Group};
    setup() {
        super.setup();
        this.events_groups = useState([]);
        this.titles = useState([]);
        this.orm = useService("orm");
        useRecordObserver(this.willUpdateRecord.bind(this));
        
    }
    async willUpdateRecord(record) {
        console.log(record);
        var events_details = await this.orm.searchRead(
            'customisable_workflow_report.work_doc_event',
            [
                ['id', 'in', record.data.document_event_ids._currentIds]
            ],
            ['document_id', 'type', 'create_date', 'create_user_id', 'date', 'user_id', 'reference', 'step_id', 'res_id', 
                'document_model', 'model', 'current_user_can_act', 'source_attachment', 'source_mimetype', 'source_previewable',
                'source_attachment_pdf', 'result_attachment', 'result_mimetype', 'result_previewable',
                'result_attachment_pdf', 'state', 'group_name', 'version_number'
            ],
        );
        var groups = {};
        events_details.forEach(detail =>  {
            if (!groups[detail.group_name]) {
                groups[detail.group_name] = {
                    group: [detail.document_id[0],detail.group_name],
                    events: []
                };
            }
            groups[detail.group_name].events.push(detail);
        });
        this.events_groups.splice(0, this.events_groups.length);
        this.titles.splice(0, this.titles.length);
        for (let key in groups) {
            this.events_groups.push(groups[key]);
            this.titles.push(groups[key].group[1]);
        }
    }
    
};

DocumentEventWidget.template = "customisable_workflow_report.DocumentEventWidget";

export const documentEventWidget = {
    component: DocumentEventWidget,
};
registry.category("fields").add("document_event_widget", documentEventWidget);