function DataTable({ columns, rows, emptyMessage = "No data available." }) {
    if (!rows || rows.length === 0) {
        return <p className="text-sm text-[#7b8395] py-3">{emptyMessage}</p>;
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
                <thead>
                    <tr className="border-b border-[#1f2533] text-left text-[#7b8395]">
                        {columns.map((col) => (
                            <th key={col.key} className="py-2 pr-4 font-medium">
                                {col.label}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, i) => (
                        <tr key={i} className="border-b border-[#1f2533]/60 hover:bg-[#161b28]">
                            {columns.map((col) => (
                                <td key={col.key} className="py-2 pr-4 text-[#c5cad6]">
                                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default DataTable;