var dag = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});
const OPT=(v)=>{return React.createElement('option',Object.assign({},v,{key:v.value}))}

dag.DeleteRow = function (props) {
    return React.createElement(
        'button',
        {
            className: "btn btn-outline-secondary btn-sm",
            onClick: function() {
                props.api.applyTransaction({ remove: [props.data] });
            }
        },
        React.createElement("i", { className: "bi bi-trash3-fill" })
    );
};
dag.SelectRow = function (props) {
    const {setData, _} = props;

    const handleChange = function(event) {
        const val = event.target.value;
        props.node.setDataValue(props.column.colId, val);
        setData(val)
    };
    return React.createElement(
        'select',
        {value: props.value || '', onChange: handleChange, class: "grid-select"},
        [OPT({"label": '', "value": ''})].concat(props.options.map(option =>OPT(option)))
    );
};

dag.CustomNoRowsOverlay=function(){return React.createElement('div',{},'')};
