

define i32 @func.aa(i32* %b.ptr, i32 %n) {
    %n.ptr = alloca i32
    store i32 %n, i32* %n.ptr
    store i32 5, i32* %n.ptr
    %n.1 = load i32, i32* %n.ptr
    ret i32 %n.1
}

define i32 @main() {
    %d.ptr = alloca [3 x i32]
    %res.ptr = alloca i32
    %d.2.ptr = getelementptr inbounds [3 x i32], [3 x i32]* %d.ptr, i32 0, i32 0
    %aa.3 = call i32 @func.aa(i32* %d.2.ptr, i32 2)
    store i32 %aa.3, i32* %res.ptr
    ret i32 0
}

declare i32 @printf(i8*, ...)
