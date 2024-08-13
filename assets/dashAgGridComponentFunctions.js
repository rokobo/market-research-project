var dag = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

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

dag.CustomNoRowsOverlay=function(){return React.createElement('div',{},'')};
